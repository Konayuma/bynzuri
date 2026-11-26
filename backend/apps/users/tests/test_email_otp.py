from datetime import timedelta
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import EmailVerification
from apps.users.verification import code_for, process_verification_email

pytestmark = pytest.mark.django_db


def register(client):
    return client.post('/api/auth/register/', {'email': 'New@example.com', 'password': 'strongpass123', 'first_name': 'Ada'}, format='json')


@override_settings(RESEND_API_KEY='test-key')
def test_registration_sends_code_and_requires_verification_before_login():
    client = APIClient()
    response = register(client)
    assert response.status_code == 201
    user = get_user_model().objects.get(email='new@example.com')
    challenge = EmailVerification.objects.get(user=user)
    code = code_for(challenge)
    assert not user.is_active and code not in str(response.data) and code not in challenge.nonce
    login = {'email': user.email, 'password': 'strongpass123'}
    assert client.post('/api/auth/token/', login, format='json').status_code == 401
    sent = Mock(ok=True, status_code=200); sent.json.return_value = {'id': 'mail-1'}
    with patch('apps.users.verification.requests.post', return_value=sent) as post:
        assert process_verification_email()
    assert code in post.call_args.kwargs['json']['text']
    assert post.call_args.kwargs['json']['to'] == [user.email]
    assert client.post('/api/auth/verify-email/', {'email': user.email, 'code': code}, format='json').status_code == 200
    assert client.post('/api/auth/verify-email/', {'email': user.email, 'code': code}, format='json').status_code == 400
    assert client.post('/api/auth/token/', login, format='json').status_code == 200


def test_wrong_expired_and_replaced_codes_cannot_activate_account():
    client = APIClient(); register(client)
    challenge = EmailVerification.objects.get(user__email='new@example.com')
    code = code_for(challenge)
    original_nonce = challenge.nonce
    incorrect = '999999' if code != '999999' else '000000'
    for _ in range(5):
        assert client.post('/api/auth/verify-email/', {'email': challenge.user.email, 'code': incorrect}, format='json').status_code == 400
    assert client.post('/api/auth/verify-email/', {'email': challenge.user.email, 'code': code}, format='json').status_code == 400
    challenge.sent_requested_at = timezone.now() - timedelta(minutes=2)
    challenge.save(update_fields=['sent_requested_at'])
    assert client.post('/api/auth/resend-verification/', {'email': challenge.user.email}, format='json').status_code == 200
    challenge.refresh_from_db()
    assert challenge.nonce != original_nonce
    challenge.expires_at = timezone.now() - timedelta(seconds=1)
    challenge.save(update_fields=['expires_at'])
    assert client.post('/api/auth/verify-email/', {'email': challenge.user.email, 'code': code_for(challenge)}, format='json').status_code == 400
    challenge.user.refresh_from_db()
    assert not challenge.user.is_active


@override_settings(RESEND_API_KEY='test-key')
def test_failed_delivery_is_queued_for_retry_without_exposing_code():
    client = APIClient(); register(client)
    rejected = Mock(ok=False, status_code=429); rejected.json.return_value = {}
    with patch('apps.users.verification.requests.post', return_value=rejected):
        assert process_verification_email()
    challenge = EmailVerification.objects.get(user__email='new@example.com')
    assert challenge.status == 'pending' and challenge.next_attempt_at > timezone.now()
    assert code_for(challenge) not in challenge.last_error


@override_settings(RESEND_API_KEY='test-key')
def test_existing_cron_command_processes_verification_queue():
    client = APIClient(); register(client)
    sent = Mock(ok=True, status_code=200); sent.json.return_value = {'id': 'mail-2'}
    with patch('apps.users.verification.requests.post', return_value=sent):
        call_command('process_order_emails', limit=10)
    assert EmailVerification.objects.get(user__email='new@example.com').status == 'sent'
