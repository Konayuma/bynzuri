import pytest
from rest_framework import status
from decimal import Decimal
from apps.payments.models import Payment
from apps.orders.models import Order


@pytest.mark.django_db
class TestPaymentModel:
    def test_create_payment(self, order):
        payment = Payment.objects.create(
            order=order,
            user=order.user,
            method='mtn_momo',
            amount=order.grand_total,
            idempotency_key='test-key-001'
        )
        assert payment.status == 'pending'
        assert payment.method == 'mtn_momo'
        assert str(payment) == f'mtn_momo - pending - {order.grand_total}'

    def test_payment_idempotency_key_unique(self, order):
        Payment.objects.create(
            order=order, user=order.user, method='visa',
            amount=Decimal('100'), idempotency_key='unique-key'
        )
        with pytest.raises(Exception):
            Payment.objects.create(
                order=order, user=order.user, method='mastercard',
                amount=Decimal('100'), idempotency_key='unique-key'
            )

    def test_payment_status_transitions(self, order):
        payment = Payment.objects.create(
            order=order, user=order.user, method='airtel_money',
            amount=order.grand_total, idempotency_key='transition-key'
        )
        payment.status = 'success'
        payment.transaction_reference = 'TXN-001'
        payment.save()
        payment.refresh_from_db()
        assert payment.status == 'success'


@pytest.mark.django_db
class TestPaymentAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()

    def test_initiate_payment(self, user, order):
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/payments/initiate/', {
            'order_id': str(order.id),
            'method': 'mtn_momo'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['method'] == 'mtn_momo'
        assert 'payment_url' in response.data

    def test_initiate_payment_for_processed_order(self, user, order):
        order.status = 'paid'
        order.save()
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/payments/initiate/', {
            'order_id': str(order.id),
            'method': 'mtn_momo'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_payment_webhook_success(self, user, order):
        from apps.payments.models import Payment
        payment = Payment.objects.create(
            order=order, user=user, method='visa',
            amount=order.grand_total, idempotency_key='webhook-key-1'
        )
        response = self.client.post('/api/payments/webhook/', {
            'transaction_reference': 'TXN-WEB-001',
            'status': 'success',
            'idempotency_key': 'webhook-key-1'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

        payment.refresh_from_db()
        assert payment.status == 'success'
        order.refresh_from_db()
        assert order.status == 'paid'

    def test_payment_webhook_idempotent(self, user, order):
        from apps.payments.models import Payment
        Payment.objects.create(
            order=order, user=user, method='mtn_momo',
            amount=order.grand_total, idempotency_key='webhook-key-2',
            status='success'
        )
        response = self.client.post('/api/payments/webhook/', {
            'transaction_reference': 'TXN-WEB-002',
            'status': 'success',
            'idempotency_key': 'webhook-key-2'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'already_processed'
