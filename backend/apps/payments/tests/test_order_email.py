from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
import requests
from django.test import override_settings
from django.utils import timezone

from apps.orders.email_notifications import email_content, process_one, queue_order_created
from apps.orders.models import OrderEmail, OrderItem
from apps.orders.services import transition_order
from apps.payments.models import Payment
from apps.payments.views import apply_provider_result

pytestmark = pytest.mark.django_db


def provider_result(payment, status='successful', amount=None):
    return {'reference': payment.idempotency_key, 'currency': payment.currency,
            'amount': str(amount if amount is not None else payment.amount), 'status': status}


@override_settings(ORDER_NOTIFICATION_EMAIL='hairskin@bynzuri.com')
def test_payment_receipt_is_only_queued_after_matching_success_and_once(user, order):
    payment = Payment.objects.create(order=order, user=user, method='mtn_momo',
        amount=order.grand_total, idempotency_key='successful-payment')
    assert not apply_provider_result(payment.pk, provider_result(payment, amount=Decimal('1.00')))
    assert not OrderEmail.objects.exists()
    assert apply_provider_result(payment.pk, provider_result(payment))
    assert apply_provider_result(payment.pk, provider_result(payment))
    assert set(OrderEmail.objects.values_list('event', flat=True)) == {'payment_receipt', 'owner_paid'}
    assert OrderEmail.objects.get(event='payment_receipt').recipient == user.email
    assert OrderEmail.objects.get(event='owner_paid').recipient == 'hairskin@bynzuri.com'
    order.refresh_from_db()
    assert order.status == 'paid'


@override_settings(ORDER_NOTIFICATION_EMAIL='hairskin@bynzuri.com')
def test_early_confirmation_is_explicitly_unpaid_and_details_are_escaped(user, order):
    order.notes = 'Please call before delivery'
    order.save(update_fields=['notes'])
    OrderItem.objects.create(order=order, product_title='<Oil & cream>', quantity=2,
                             price_at_purchase=Decimal('100.00'))
    queue_order_created(order)
    queue_order_created(order)
    assert OrderEmail.objects.count() == 2
    customer = OrderEmail.objects.get(event='order_received')
    subject, text, html = email_content(customer)
    assert 'payment pending' in subject
    assert 'Not confirmed' in text and 'ZMW 235.00' in text
    assert '&lt;Oil &amp; cream&gt;' in html and '<Oil & cream>' not in html
    assert order.street_address not in text
    _, owner_text, _ = email_content(OrderEmail.objects.get(event='owner_order'))
    assert order.street_address in owner_text
    assert 'Please call before delivery' in owner_text


@override_settings(RESEND_API_KEY='test-key', RESEND_FROM_EMAIL='HairSkin <orders@bynzuri.com>',
                   RESEND_REPLY_TO='hairskin@bynzuri.com', ORDER_NOTIFICATION_EMAIL='hairskin@bynzuri.com')
def test_delivery_retries_rate_limit_with_stable_key_and_records_provider_id(user, order):
    queue_order_created(order)
    row = OrderEmail.objects.get(event='order_received')
    OrderEmail.objects.exclude(pk=row.pk).delete()
    throttled = Mock(ok=False, status_code=429)
    sent = Mock(ok=True, status_code=200); sent.json.return_value = {'id': 'resend-id'}
    with patch('apps.orders.email_notifications.requests.post', side_effect=[throttled, sent]) as post:
        assert process_one()
        row.refresh_from_db()
        assert row.status == 'pending' and row.next_attempt_at > timezone.now()
        OrderEmail.objects.filter(pk=row.pk).update(next_attempt_at=timezone.now() - timedelta(seconds=1))
        assert process_one()
    row.refresh_from_db()
    assert row.status == 'sent' and row.provider_id == 'resend-id' and row.attempts == 2
    assert post.call_args_list[0].kwargs['headers']['Idempotency-Key'] == post.call_args_list[1].kwargs['headers']['Idempotency-Key']
    assert post.call_args_list[0].kwargs['json'] == post.call_args_list[1].kwargs['json']


@override_settings(RESEND_API_KEY='test-key')
def test_timeout_retries_then_stops_before_provider_idempotency_expires(user, order):
    queue_order_created(order)
    row = OrderEmail.objects.get(event='order_received')
    OrderEmail.objects.exclude(pk=row.pk).delete()
    with patch('apps.orders.email_notifications.requests.post', side_effect=requests.Timeout):
        assert process_one()
    row.refresh_from_db()
    assert row.status == 'pending'
    OrderEmail.objects.filter(pk=row.pk).update(first_attempt_at=timezone.now()-timedelta(hours=24), next_attempt_at=timezone.now()-timedelta(seconds=1))
    with patch('apps.orders.email_notifications.requests.post') as post:
        assert process_one()
        post.assert_not_called()
    row.refresh_from_db()
    assert row.status == 'needs_review'


@override_settings(RESEND_API_KEY='')
def test_missing_configuration_leaves_messages_queued(user, order):
    queue_order_created(order)
    assert not process_one()
    assert OrderEmail.objects.filter(status='pending').count() == 2


def test_dispatch_and_delivery_notifications_are_queued_once(user, order):
    order.status = 'processing'; order.save(update_fields=['status'])
    transition_order(order.pk, 'dispatched')
    transition_order(order.pk, 'dispatched')
    transition_order(order.pk, 'delivered')
    assert list(OrderEmail.objects.values_list('event', flat=True)) == ['order_dispatched', 'order_delivered']


@override_settings(RESEND_API_KEY='test-key')
def test_permanent_provider_error_is_marked_for_review_without_blocking_other_email(user, order):
    queue_order_created(order)
    rejected = Mock(ok=False, status_code=403)
    rejected.json.return_value = {'name': 'invalid_api_key'}
    sent = Mock(ok=True, status_code=200)
    sent.json.return_value = {'id': 'accepted-id'}
    with patch('apps.orders.email_notifications.requests.post', side_effect=[rejected, sent]):
        assert process_one()
        assert process_one()
    assert OrderEmail.objects.filter(status='needs_review').count() == 1
    assert OrderEmail.objects.filter(status='sent').count() == 1


def test_failed_payment_never_queues_receipt(user, order):
    payment = Payment.objects.create(order=order, user=user, method='mtn_momo',
        amount=order.grand_total, idempotency_key='failed-payment')
    assert apply_provider_result(payment.pk, provider_result(payment, status='failed'))
    assert not OrderEmail.objects.exists()
