from datetime import timedelta
from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock, patch
import re

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import PasswordResetRequest, SupportInquiry
from apps.users.password_reset import process_password_reset_email
from apps.users.support import process_support_inquiry_email

pytestmark = pytest.mark.django_db
User = get_user_model()


@override_settings(
    RESEND_API_KEY='test-key',
    PUBLIC_SITE_URL='https://www.bynzuri.com',
    RESEND_FROM_EMAIL='HairSkin by Nzuri <hairskincare@bynzuri.com>',
    RESEND_REPLY_TO='hairskincare@bynzuri.com',
)
def test_forgot_password_queues_and_sends_working_reset_link_via_resend():
    user = User.objects.create_user(
        username='resetme@example.com',
        email='resetme@example.com',
        password='oldpassword123',
        first_name='Mwamba',
        is_active=True,
    )
    client = APIClient()

    # Even if an untrusted redirect_url is supplied, the link must use PUBLIC_SITE_URL.
    response = client.post(
        '/api/auth/forgot-password/',
        {'email': 'ResetMe@example.com', 'redirect_url': 'https://evil.example/auth/reset-password'},
        format='json',
    )
    assert response.status_code == 200
    reset_req = PasswordResetRequest.objects.get(user=user)
    assert reset_req.status == 'pending'

    sent = Mock(ok=True, status_code=200)
    sent.json.return_value = {'id': 'resend-reset-1'}
    with patch('apps.users.password_reset.requests.post', return_value=sent) as post:
        call_command('process_order_emails', limit=10)

    assert post.call_count == 1
    payload = post.call_args.kwargs['json']
    assert payload['to'] == ['resetme@example.com']
    assert payload['subject'] == 'Reset your By Nzuri password'
    assert 'cid:bynzuri-logo' in payload['html']
    assert payload['attachments'][0]['content_id'] == 'bynzuri-logo'
    assert 'evil.example' not in payload['text']
    assert '/auth/reset-password/auth/reset-password' not in payload['text']

    match = re.search(r'https://www\.bynzuri\.com/auth/reset-password\?[^\s]+', payload['text'])
    assert match is not None
    parsed = urlparse(match.group(0))
    params = parse_qs(parsed.query)
    uid = params['uid'][0]
    token = params['token'][0]

    reset_req.refresh_from_db()
    assert reset_req.status == 'sent'
    assert reset_req.provider_id == 'resend-reset-1'

    # Completing the reset with the emailed link updates the password and invalidates reuse.
    confirm = client.post(
        '/api/auth/reset-password/',
        {'uid': uid, 'token': token, 'new_password': 'newpassword456'},
        format='json',
    )
    assert confirm.status_code == 200
    reset_req.refresh_from_db()
    assert reset_req.status == 'expired'

    # Token cannot be reused
    reuse = client.post(
        '/api/auth/reset-password/',
        {'uid': uid, 'token': token, 'new_password': 'anotherpassword789'},
        format='json',
    )
    assert reuse.status_code == 400

    # New password works for sign-in, old password does not
    assert client.post('/api/auth/token/', {'email': user.email, 'password': 'oldpassword123'}, format='json').status_code == 401
    assert client.post('/api/auth/token/', {'email': user.email, 'password': 'newpassword456'}, format='json').status_code == 200


def test_forgot_password_ignores_unknown_or_inactive_user_and_enforces_cooldown():
    client = APIClient()

    # Unknown email returns generic 200 and queues nothing
    assert client.post('/api/auth/forgot-password/', {'email': 'nobody@example.com'}, format='json').status_code == 200
    assert PasswordResetRequest.objects.count() == 0

    # Inactive (unverified) user returns generic 200 and queues nothing
    User.objects.create_user(
        username='inactive@example.com',
        email='inactive@example.com',
        password='oldpassword123',
        is_active=False,
    )
    assert client.post('/api/auth/forgot-password/', {'email': 'inactive@example.com'}, format='json').status_code == 200
    assert PasswordResetRequest.objects.count() == 0

    # Active user gets queued and respects 60s cooldown
    active = User.objects.create_user(
        username='active@example.com',
        email='active@example.com',
        password='oldpassword123',
        is_active=True,
    )
    assert client.post('/api/auth/forgot-password/', {'email': active.email}, format='json').status_code == 200
    req = PasswordResetRequest.objects.get(user=active)
    original_nonce = req.nonce

    # Immediate repeat does not replace nonce
    assert client.post('/api/auth/forgot-password/', {'email': active.email}, format='json').status_code == 200
    req.refresh_from_db()
    assert req.nonce == original_nonce

    # After cooldown, a new request refreshes nonce and re-queues
    req.sent_requested_at = timezone.now() - timedelta(minutes=2)
    req.status = 'sent'
    req.save(update_fields=['sent_requested_at', 'status'])
    assert client.post('/api/auth/forgot-password/', {'email': active.email}, format='json').status_code == 200
    req.refresh_from_db()
    assert req.nonce != original_nonce
    assert req.status == 'pending'


@override_settings(RESEND_API_KEY='test-key')
def test_password_reset_delivery_retry_on_429():
    user = User.objects.create_user(
        username='retry@example.com',
        email='retry@example.com',
        password='oldpassword123',
        is_active=True,
    )
    client = APIClient()
    client.post('/api/auth/forgot-password/', {'email': user.email}, format='json')

    rejected = Mock(ok=False, status_code=429)
    rejected.json.return_value = {}
    with patch('apps.users.password_reset.requests.post', return_value=rejected):
        assert process_password_reset_email()

    req = PasswordResetRequest.objects.get(user=user)
    assert req.status == 'pending'
    assert req.next_attempt_at > timezone.now()


@override_settings(
    RESEND_API_KEY='test-key',
    ORDER_NOTIFICATION_EMAIL='hairskincare@bynzuri.com',
    SUPPORT_NOTIFICATION_EMAIL='hairskincare@bynzuri.com',
    RESEND_FROM_EMAIL='HairSkin by Nzuri <hairskincare@bynzuri.com>',
)
def test_support_inquiry_creates_record_and_sends_to_support_email():
    client = APIClient()
    response = client.post(
        '/api/support/inquiries/',
        {
            'name': 'Chanda Banda',
            'email': 'Chanda@example.com',
            'phone': '+260977123456',
            'topic': 'order',
            'order_reference': 'ORD-1234',
            'subject': 'Delivery timing for Lusaka',
            'message': 'Hi team, could you confirm when my order will arrive in Kabulonga?',
        },
        format='json',
    )
    assert response.status_code == 201
    assert response.data['reference'].startswith('SUP-')
    inquiry = SupportInquiry.objects.get(pk=response.data['id'])
    assert inquiry.email == 'chanda@example.com'
    assert inquiry.status == 'pending'

    sent = Mock(ok=True, status_code=200)
    sent.json.return_value = {'id': 'resend-support-1'}
    with patch('apps.users.support.requests.post', return_value=sent) as post:
        call_command('process_order_emails', limit=10)

    assert post.call_count == 1
    payload = post.call_args.kwargs['json']
    assert payload['to'] == ['hairskincare@bynzuri.com']
    assert payload['reply_to'] == 'chanda@example.com'
    assert 'Order & Delivery' in payload['subject']
    assert inquiry.reference in payload['subject']
    assert 'ORD-1234' in payload['text']
    assert '+260977123456' in payload['text']
    assert 'Kabulonga' in payload['text']
    assert 'cid:bynzuri-logo' in payload['html']

    inquiry.refresh_from_db()
    assert inquiry.status == 'sent'
    assert inquiry.provider_id == 'resend-support-1'


def test_support_inquiry_validation_and_honeypot():
    client = APIClient()

    # Invalid/short payload rejected
    bad = client.post(
        '/api/support/inquiries/',
        {'name': 'A', 'email': 'not-an-email', 'subject': 'Hi', 'message': 'Too short'},
        format='json',
    )
    assert bad.status_code == 400
    assert SupportInquiry.objects.count() == 0

    # Honeypot filled -> accepted silently without storing or queuing email
    bot = client.post(
        '/api/support/inquiries/',
        {
            'name': 'Bot User',
            'email': 'bot@example.com',
            'topic': 'general',
            'subject': 'Buy spam',
            'message': 'This is an automated spam submission.',
            'website': 'https://spam.example',
        },
        format='json',
    )
    assert bot.status_code == 201
    assert SupportInquiry.objects.count() == 0


@override_settings(
    RESEND_API_KEY='test-key',
    SUPPORT_NOTIFICATION_EMAIL='hairskincare@bynzuri.com',
)
def test_support_inquiry_retry_on_provider_error():
    client = APIClient()
    res = client.post(
        '/api/support/inquiries/',
        {
            'name': 'Lombe Phiri',
            'email': 'lombe@example.com',
            'topic': 'product',
            'subject': 'Hair oil recommendation',
            'message': 'Which oil works best for dry scalp and protective styles?',
        },
        format='json',
    )
    assert res.status_code == 201

    failed = Mock(ok=False, status_code=503)
    failed.json.return_value = {}
    with patch('apps.users.support.requests.post', return_value=failed):
        assert process_support_inquiry_email()

    inquiry = SupportInquiry.objects.get(pk=res.data['id'])
    assert inquiry.status == 'pending'
    assert inquiry.next_attempt_at > timezone.now()
