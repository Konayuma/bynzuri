"""Email verification codes and the durable scheduled delivery queue."""
import hashlib
import hmac
import secrets
from datetime import timedelta

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from .models import EmailVerification

CODE_LIFETIME = timedelta(minutes=30)
RESEND_DELAY = timedelta(seconds=60)
MAX_ATTEMPTS = 5


def code_for(challenge):
    digest = hmac.new(settings.SECRET_KEY.encode(), f'email-otp:{challenge.user_id}:{challenge.nonce}'.encode(), hashlib.sha256).digest()
    return f'{int.from_bytes(digest, "big") % 1000000:06d}'


def issue_code(user):
    now = timezone.now()
    challenge, _ = EmailVerification.objects.update_or_create(user=user, defaults={
        'nonce': secrets.token_hex(32), 'expires_at': now + CODE_LIFETIME,
        'attempts': 0, 'sent_requested_at': now, 'status': 'pending',
        'send_attempts': 0, 'first_attempt_at': None, 'next_attempt_at': None,
        'lease_until': None, 'provider_id': '', 'last_error': '',
    })
    return challenge


def process_verification_email():
    if not settings.RESEND_API_KEY:
        return False
    now = timezone.now()
    with transaction.atomic():
        challenge = (EmailVerification.objects.select_for_update(skip_locked=True, of=('self',)).select_related('user')
            .filter(Q(status='pending', next_attempt_at__isnull=True) | Q(status='pending', next_attempt_at__lte=now) |
                    Q(status='sending', lease_until__lt=now)).order_by('sent_requested_at').first())
        if not challenge:
            return False
        if (
            challenge.expires_at <= now
            or challenge.user.is_active
            or (challenge.user.email_verified and challenge.user.has_usable_password())
            or challenge.attempts >= MAX_ATTEMPTS
        ):
            challenge.status = 'expired'
            challenge.save(update_fields=['status'])
            return True
        challenge.status = 'sending'
        challenge.send_attempts += 1
        challenge.first_attempt_at = challenge.first_attempt_at or now
        challenge.lease_until = now + timedelta(minutes=3)
        challenge.save(update_fields=['status', 'send_attempts', 'first_attempt_at', 'lease_until'])
        pk, nonce, attempt = challenge.pk, challenge.nonce, challenge.send_attempts
        code = code_for(challenge)
        email = challenge.user.email
        name = challenge.user.first_name
    from apps.orders.email_notifications import email_logo_attachments
    text = f'Your By Nzuri verification code is {code}. It expires 30 minutes after it was requested. If you did not create an account, you can ignore this email. Do not share this code.'
    html = render_to_string('users/verification_email.html', {'code': code, 'name': name})
    body = {'from': settings.RESEND_FROM_EMAIL, 'to': [email], 'reply_to': settings.RESEND_REPLY_TO,
            'subject': 'Your By Nzuri email verification code', 'text': text, 'html': html}
    attachments = email_logo_attachments()
    if attachments:
        body['attachments'] = attachments
    try:
        response = requests.post('https://api.resend.com/emails', json=body, timeout=20,
            headers={'Authorization': f'Bearer {settings.RESEND_API_KEY}', 'Idempotency-Key': f'verify-email/{pk}/{nonce}'})
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
            retry = response.status_code == 429 or response.status_code >= 500 or (response.status_code == 409 and error_name == 'concurrent_idempotent_requests')
            updates = {'status': 'pending' if retry else 'needs_review', 'last_error': f'Resend returned HTTP {response.status_code}'}
    except (requests.RequestException, ValueError):
        updates = {'status': 'pending', 'last_error': 'Provider request failed or response was invalid.'}
    if updates['status'] == 'pending':
        updates['next_attempt_at'] = timezone.now() + timedelta(minutes=min(5, 2 ** min(attempt, 3)))
    updates['lease_until'] = None
    EmailVerification.objects.filter(pk=pk, nonce=nonce, status='sending', send_attempts=attempt).update(**updates)
    return True
