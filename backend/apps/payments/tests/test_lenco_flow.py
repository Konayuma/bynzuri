import hashlib
import hmac
import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from apps.payments.models import Payment
from apps.payments.serializers import PaymentInitiateSerializer

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize(('phone', 'expected'), [
    ('0571234567', '260571234567'), ('0771234567', '260771234567'),
    ('0971234567', '260971234567'), ('+260 571 234 567', '260571234567'),
    ('260771234567', '260771234567'),
])
def test_payment_phone_formats(phone, expected):
    serializer = PaymentInitiateSerializer(data={'order_id': '00000000-0000-0000-0000-000000000001', 'method': 'airtel_money', 'phone': phone})
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['phone'] == expected


@pytest.fixture(autouse=True)
def lenco_settings():
    with override_settings(LENCO_API_KEY='test-token'):
        yield


def result(payment, state='successful', **overrides):
    return {'reference': payment.idempotency_key, 'amount': str(payment.amount), 'currency': 'ZMW', 'status': state, **overrides}


def signed(client, payload, signature=None):
    body = json.dumps(payload).encode()
    key = hashlib.sha256(b'test-token').hexdigest()
    signature = signature or hmac.new(key.encode(), body, hashlib.sha512).hexdigest()
    return client.post('/api/payments/webhook/', data=body, content_type='application/json', HTTP_X_LENCO_SIGNATURE=signature)


def test_mtn_initiation_is_idempotent(user, order):
    client = APIClient(); client.force_authenticate(user)
    with patch('apps.payments.views.lenco_service.initiate_collection', return_value={'status': False, 'uncertain': True}) as send:
        payload = {'order_id': str(order.id), 'method': 'mtn_momo', 'phone': '0971111111'}
        first = client.post('/api/payments/initiate/', payload, format='json')
        second = client.post('/api/payments/initiate/', {**payload, 'method': 'airtel_money'}, format='json')
    assert first.status_code == 201 and second.status_code == 200
    assert first.data['id'] == second.data['id'] and first.data['status'] == 'pending'
    assert send.call_count == 1
    assert Payment.objects.get().phone == '260971111111'


def test_restricts_methods_and_unconfigured(user, order):
    client = APIClient(); client.force_authenticate(user)
    data = {'order_id': str(order.id), 'method': 'zamtel_money', 'phone': '0971111111'}
    assert client.post('/api/payments/initiate/', data, format='json').status_code == 400
    with override_settings(LENCO_API_KEY=''):
        assert client.post('/api/payments/initiate/', {**data, 'method': 'mtn_momo'}, format='json').status_code == 503
    assert not Payment.objects.exists()


def test_signed_webhook_validates_details_and_is_idempotent(user, order):
    payment = Payment.objects.create(order=order, user=user, method='airtel_money', operator='airtel', amount=order.grand_total, idempotency_key='reference1')
    client = APIClient()
    data = result(payment)
    assert signed(client, {'event': 'collection.successful', 'data': data}, 'wrong').status_code == 401
    assert signed(client, {'event': 'collection.successful', 'data': {**data, 'amount': '1.00'}}).status_code == 400
    order.refresh_from_db(); assert order.status == 'awaiting_payment'
    assert signed(client, {'event': 'collection.successful', 'data': data}).status_code == 200
    assert signed(client, {'event': 'collection.successful', 'data': data}).status_code == 200
    assert signed(client, {'event': 'collection.failed', 'data': result(payment, 'failed')}).status_code == 200
    payment.refresh_from_db(); order.refresh_from_db()
    assert payment.status == 'success' and order.status == 'paid'


def test_status_reconciles_latest_attempt_without_regressing_order(user, order):
    Payment.objects.create(order=order, user=user, method='mtn_momo', amount=order.grand_total, idempotency_key='old', status='failed')
    payment = Payment.objects.create(order=order, user=user, method='airtel_money', amount=order.grand_total, idempotency_key='new')
    client = APIClient(); client.force_authenticate(user)
    with patch('apps.payments.views.lenco_service.get_collection_status', return_value={'status': True, 'data': result(payment)}):
        response = client.get(f'/api/payments/status/{order.id}/')
    assert response.status_code == 200 and response.data['status'] == 'success'
    order.refresh_from_db(); assert order.status == 'paid'


def test_status_reports_provider_lookup_failure_without_marking_payment_failed(user, order):
    payment = Payment.objects.create(order=order, user=user, method='mtn_momo', amount=order.grand_total, idempotency_key='unknown')
    client = APIClient(); client.force_authenticate(user)
    with patch('apps.payments.views.lenco_service.get_collection_status', return_value={'status': False, 'access_denied': True}):
        response = client.get(f'/api/payments/status/{order.id}/')
    assert response.status_code == 200
    assert response.data['status'] == 'pending'
    assert response.data['verification_unavailable'] is True
    payment.refresh_from_db()
    assert payment.status == 'pending'


def test_webhook_handles_malformed_mobile_details(user, order):
    payment = Payment.objects.create(order=order, user=user, method='mtn_momo', amount=order.grand_total, idempotency_key='details')
    client = APIClient()
    response = signed(client, {'event': 'collection.successful', 'data': result(payment, mobileMoneyDetails='unavailable')})
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == 'success'
    assert payment.account_name == ''


def test_failed_attempt_can_retry_but_other_users_cannot_access(user, order):
    failed = Payment.objects.create(order=order, user=user, method='mtn_momo', amount=order.grand_total, idempotency_key='failed-attempt', status='failed')
    client = APIClient(); client.force_authenticate(user)
    with patch('apps.payments.views.lenco_service.initiate_collection', return_value={'status': False, 'uncertain': True}):
        response = client.post('/api/payments/initiate/', {'order_id': str(order.id), 'method': 'airtel_money', 'phone': '+260971111111'}, format='json')
    assert response.status_code == 201 and response.data['id'] != str(failed.id)
    assert response.data['method'] == 'airtel_money'
    client.force_authenticate(user=None)
    assert client.get(f'/api/payments/status/{order.id}/').status_code == 401
