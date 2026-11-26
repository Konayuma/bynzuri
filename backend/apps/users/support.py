"""Support inquiry email delivery worker via Resend."""
from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from .models import SupportInquiry


def support_email_content(inquiry):
    topic_label = inquiry.get_topic_display()
    reference = inquiry.reference
    subject = f"By Nzuri Support [{topic_label}]: {inquiry.subject} ({reference})"
    lines = [
        f"New customer inquiry ({reference})",
        "",
        f"From: {inquiry.name} <{inquiry.email}>",
        f"Topic: {topic_label}",
    ]
    if inquiry.phone:
        lines.append(f"Phone / WhatsApp: {inquiry.phone}")
    if inquiry.order_reference:
        lines.append(f"Order number: {inquiry.order_reference}")
    lines += [
        f"Subject: {inquiry.subject}",
        "",
        "Message:",
        inquiry.message,
        "",
        "Reply directly to this email to respond to the customer.",
        "HairSkin by Nzuri",
    ]
    text = '\n'.join(lines)
    html = render_to_string(
        'users/support_inquiry_email.html',
        {
            'inquiry': inquiry,
            'topic_label': topic_label,
            'reference': reference,
        },
    )
    return subject, text, html


def process_support_inquiry_email():
    if not settings.RESEND_API_KEY:
        return False
    recipient = getattr(settings, 'SUPPORT_NOTIFICATION_EMAIL', '') or settings.ORDER_NOTIFICATION_EMAIL
    if not recipient:
        return False
    now = timezone.now()
    with transaction.atomic():
        inquiry = (
            SupportInquiry.objects.select_for_update(skip_locked=True)
            .filter(
                Q(status='pending', next_attempt_at__isnull=True)
                | Q(status='pending', next_attempt_at__lte=now)
                | Q(status='sending', lease_until__lt=now)
            )
            .order_by('created_at')
            .first()
        )
        if not inquiry:
            return False
        if inquiry.first_attempt_at and now - inquiry.first_attempt_at >= timedelta(hours=23):
            inquiry.status = 'needs_review'
            inquiry.last_error = 'Retry window expired; check the provider before resending.'
            inquiry.save(update_fields=['status', 'last_error'])
            return True
        inquiry.status = 'sending'
        inquiry.first_attempt_at = inquiry.first_attempt_at or now
        inquiry.send_attempts += 1
        inquiry.lease_until = now + timedelta(minutes=3)
        inquiry.save(update_fields=['status', 'first_attempt_at', 'send_attempts', 'lease_until'])
        inquiry_id, attempt = inquiry.pk, inquiry.send_attempts

    from apps.orders.email_notifications import email_logo_attachments

    subject, text, html = support_email_content(inquiry)
    body = {
        'from': settings.RESEND_FROM_EMAIL,
        'to': [recipient],
        'reply_to': inquiry.email,
        'subject': subject,
        'text': text,
        'html': html,
    }
    attachments = email_logo_attachments()
    if attachments:
        body['attachments'] = attachments

    try:
        response = requests.post(
            'https://api.resend.com/emails',
            json=body,
            timeout=20,
            headers={
                'Authorization': f'Bearer {settings.RESEND_API_KEY}',
                'Idempotency-Key': f'support-inquiry/{inquiry_id}',
            },
        )
        if response.ok:
            provider_id = response.json().get('id')
            if not provider_id:
                raise ValueError('Missing provider ID')
            updates = {'status': 'sent', 'provider_id': str(provider_id), 'last_error': ''}
        else:
            try:
                error_name = response.json().get('name', '')
            except (ValueError, AttributeError):
                error_name = ''
            retry = (
                response.status_code == 429
                or response.status_code >= 500
                or (response.status_code == 409 and error_name == 'concurrent_idempotent_requests')
            )
            updates = {
                'status': 'pending' if retry else 'needs_review',
                'last_error': f'Resend returned HTTP {response.status_code}',
            }
    except (requests.RequestException, ValueError):
        updates = {'status': 'pending', 'last_error': 'Provider request failed or response was invalid.'}

    if updates['status'] == 'pending':
        updates['next_attempt_at'] = timezone.now() + timedelta(minutes=min(60, 2 ** min(attempt, 6)))
    updates['lease_until'] = None
    SupportInquiry.objects.filter(pk=inquiry_id, status='sending', send_attempts=attempt).update(**updates)
    return True
