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
    assert 'cid:bynzuri-logo' in post.call_args.kwargs['json']['html']
    assert post.call_args.kwargs['json']['attachments'][0]['content_id'] == 'bynzuri-logo'
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


def test_reregistering_unverified_account_collapses_duplicate_and_protects_password():
    client = APIClient()
    first = register(client)
    assert first.status_code == 201
    User = get_user_model()
    assert User.objects.filter(email='new@example.com').count() == 1
    challenge = EmailVerification.objects.get(user__email='new@example.com')
    first_nonce = challenge.nonce

    # Retry with same password within resend window: reuses account without creating duplicate
    retry = client.post('/api/auth/register/', {'email': 'new@example.com', 'password': 'strongpass123', 'first_name': 'Ada', 'last_name': 'Lovelace'}, format='json')
    assert retry.status_code == 201
    assert User.objects.filter(email='new@example.com').count() == 1
    user = User.objects.get(email='new@example.com')
    assert user.last_name == 'Lovelace'
    challenge.refresh_from_db()
    assert challenge.nonce == first_nonce

    # Retry with different password: does not overwrite password, returns unverified_account_exists
    mismatch = client.post('/api/auth/register/', {'email': 'new@example.com', 'password': 'otherpassword123', 'first_name': 'Mallory'}, format='json')
    assert mismatch.status_code == 400
    assert mismatch.data['code'] == 'unverified_account_exists'
    user.refresh_from_db()
    assert user.check_password('strongpass123')
    assert not user.check_password('otherpassword123')

    # After verification, re-registering returns account_exists
    assert client.post('/api/auth/verify-email/', {'email': user.email, 'code': code_for(challenge)}, format='json').status_code == 200
    verified_retry = register(client)
    assert verified_retry.status_code == 400
    assert verified_retry.data['code'] == 'account_exists'


def test_passwordless_registration_verifies_otp_then_sets_password_and_issues_session():
    client = APIClient()
    first = client.post('/api/auth/register/', {
        'email': 'step2@example.com',
        'first_name': 'Naomi',
        'last_name': 'Musalaba',
        'phone': '+260968018430',
    }, format='json')
    assert first.status_code == 201

    # Retrying before verification cleanly reuses the unverified account without conflict
    retry = client.post('/api/auth/register/', {
        'email': 'step2@example.com',
        'first_name': 'Naomi',
        'last_name': 'Musalaba',
        'phone': '+260968018430',
    }, format='json')
    assert retry.status_code == 201
    User = get_user_model()
    assert User.objects.filter(email='step2@example.com').count() == 1

    challenge = EmailVerification.objects.get(user__email='step2@example.com')
    verify = client.post('/api/auth/verify-email/', {'email': 'step2@example.com', 'code': code_for(challenge)}, format='json')
    assert verify.status_code == 200
    assert verify.data['requires_password'] is True
    setup_token = verify.data['setup_token']
    assert setup_token

    # Complete signup with password -> sets password, activates user, issues session cookie + access token
    complete = client.post('/api/auth/complete-signup/', {'setup_token': setup_token, 'password': 'Password123'}, format='json')
    assert complete.status_code == 200
    assert 'access' in complete.data
    assert complete.cookies['bynzuri_refresh']['httponly']

    # Setup token cannot be reused
    reuse = client.post('/api/auth/complete-signup/', {'setup_token': setup_token, 'password': 'Password456'}, format='json')
    assert reuse.status_code == 400

    # User is active and can sign in with the new password
    user = User.objects.get(email='step2@example.com')
    assert user.is_active and user.email_verified and user.check_password('Password123')


@override_settings(GOOGLE_CLIENT_ID='google-test-client-id')
def test_google_auth_creates_verified_user_and_issues_session():
    client = APIClient()
    google_resp = Mock(ok=True, status_code=200)
    google_resp.json.return_value = {
        'aud': 'google-test-client-id',
        'iss': 'https://accounts.google.com',
        'email': 'GoogleUser@example.com',
        'email_verified': 'true',
        'given_name': 'Grace',
        'family_name': 'Phiri',
        'exp': str(int(timezone.now().timestamp()) + 3600),
    }
    with patch('apps.users.session_views.requests.get', return_value=google_resp):
        response = client.post('/api/auth/google/', {'credential': 'valid-id-token'}, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert response.cookies['bynzuri_refresh']['httponly']

    User = get_user_model()
    user = User.objects.get(email='googleuser@example.com')
    assert user.is_active and user.email_verified
    assert user.first_name == 'Grace' and user.last_name == 'Phiri'
    assert not user.has_usable_password()
