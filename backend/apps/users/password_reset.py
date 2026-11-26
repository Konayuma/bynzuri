"""Password reset email outbox and Resend delivery worker."""
import secrets
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import PasswordResetRequest

RESET_LIFETIME = timedelta(minutes=60)
RESEND_DELAY = timedelta(seconds=60)
token_generator = PasswordResetTokenGenerator()


def issue_password_reset(user):
    now = timezone.now()
    reset_request, _ = PasswordResetRequest.objects.update_or_create(
        user=user,
        defaults={
            'nonce': secrets.token_hex(32),
            'expires_at': now + RESET_LIFETIME,
            'sent_requested_at': now,
            'status': 'pending',
            'send_attempts': 0,
            'first_attempt_at': None,
            'next_attempt_at': None,
            'lease_until': None,
            'provider_id': '',
            'last_error': '',
        },
    )
    return reset_request


def build_reset_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    base_url = settings.PUBLIC_SITE_URL.rstrip('/')
    return f"{base_url}/auth/reset-password?uid={uid}&token={token}"


def process_password_reset_email():
    if not settings.RESEND_API_KEY:
        return False
    now = timezone.now()
    with transaction.atomic():
        reset_request = (
            PasswordResetRequest.objects.select_for_update(skip_locked=True, of=('self',))
            .select_related('user')
            .filter(
                Q(status='pending', next_attempt_at__isnull=True)
                | Q(status='pending', next_attempt_at__lte=now)
                | Q(status='sending', lease_until__lt=now)
            )
            .order_by('sent_requested_at')
            .first()
        )
        if not reset_request:
            return False
        if reset_request.expires_at <= now or not reset_request.user.is_active:
            reset_request.status = 'expired'
            reset_request.save(update_fields=['status'])
            return True
        reset_request.status = 'sending'
        reset_request.send_attempts += 1
        reset_request.first_attempt_at = reset_request.first_attempt_at or now
        reset_request.lease_until = now + timedelta(minutes=3)
        reset_request.save(update_fields=['status', 'send_attempts', 'first_attempt_at', 'lease_until'])
        pk, nonce, attempt = reset_request.pk, reset_request.nonce, reset_request.send_attempts
        reset_url = build_reset_url(reset_request.user)
        email = reset_request.user.email
        name = reset_request.user.first_name

    from apps.orders.email_notifications import email_logo_attachments

    greeting = f"Hello {name},\n\n" if name else ""
    text = (
        f"{greeting}"
        "We received a request to reset your By Nzuri password.\n\n"
        f"Reset your password using this link:\n{reset_url}\n\n"
        "If you did not request a password reset, you can safely ignore this email — your password will not change.\n\n"
        "HairSkin by Nzuri"
    )
    html = render_to_string(
        'users/password_reset_email.html',
        {'reset_url': reset_url, 'name': name},
    )
    body = {
        'from': settings.RESEND_FROM_EMAIL,
        'to': [email],
        'reply_to': settings.RESEND_REPLY_TO,
        'subject': 'Reset your By Nzuri password',
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
                'Idempotency-Key': f'password-reset/{pk}/{nonce}',
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
        updates['next_attempt_at'] = timezone.now() + timedelta(minutes=min(5, 2 ** min(attempt, 3)))
    updates['lease_until'] = None
    PasswordResetRequest.objects.filter(
        pk=pk, nonce=nonce, status='sending', send_attempts=attempt
    ).update(**updates)
    return True
