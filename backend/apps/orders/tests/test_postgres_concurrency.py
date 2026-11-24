"""Locking tests: run only on a disposable PostgreSQL test database."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier, Event
from unittest.mock import patch
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection
from django.test import override_settings
from rest_framework.test import APIClient

from apps.cart.models import Cart, CartItem
from apps.categories.models import Category
from apps.delivery.models import DeliveryMethod
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.views import apply_provider_result
from apps.products.models import Product

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.skipif(connection.vendor != 'postgresql', reason='requires PostgreSQL row locking')]


def invoke(fn, barrier):
    close_old_connections()
    try:
        barrier.wait(timeout=10)
        return fn()
    finally:
        close_old_connections()


def test_two_checkouts_cannot_oversell_last_item():
    users = [get_user_model().objects.create_user(username=f'lock{i}@example.com', email=f'lock{i}@example.com', password='pass') for i in range(2)]
    category = Category.objects.create(name='Lock test', slug='lock-test')
    product = Product.objects.create(category=category, title='Last item', slug='last-item', price=Decimal('10'), stock=1)
    delivery = DeliveryMethod.objects.create(name='Delivery', price=Decimal('1'), estimated_days='1')
    for user in users:
        CartItem.objects.create(cart=Cart.objects.create(user=user), product=product, quantity=1)
    barrier = Barrier(2)
    def checkout(user):
        client = APIClient(); client.force_authenticate(user=user)
        data = {'checkout_key': str(uuid.uuid4()), 'province': 'Lusaka', 'town': 'Lusaka', 'street_address': 'Test', 'phone': '0971111111', 'delivery_method': str(delivery.id), 'payment_method': 'mtn_momo'}
        return client.post('/api/orders/', data, format='json').status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(invoke, lambda user=user: checkout(user), barrier) for user in users]
        statuses = sorted(f.result(timeout=20) for f in futures)
    product.refresh_from_db()
    assert statuses == [201, 400]
    assert product.stock == 0
    assert Order.objects.count() == 1


@override_settings(LENCO_API_KEY='test-token')
def test_simultaneous_initiations_share_one_payment():
    user = get_user_model().objects.create_user(username='payment@example.com', email='payment@example.com', password='pass')
    order = Order.objects.create(user=user, province='Lusaka', town='Lusaka', street_address='Test', phone='0971111111', delivery_method='test', payment_method='mtn_momo', grand_total=Decimal('10'))
    barrier = Barrier(2); provider_started = Event(); release_provider = Event()
    def provider(**kwargs):
        provider_started.set()
        if not release_provider.wait(10): raise TimeoutError('provider was not released')
        return {'status': False, 'uncertain': True}
    def initiate():
        client = APIClient(); client.force_authenticate(user=user)
        response = client.post('/api/payments/initiate/', {'order_id': str(order.id), 'method': 'mtn_momo', 'phone': '0971111111'}, format='json')
        return response.status_code, response.data['id']
    with patch('apps.payments.views.lenco_service.initiate_collection', side_effect=provider) as send:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(invoke, initiate, barrier) for _ in range(2)]
            assert provider_started.wait(10)
            # The second request must finish while the first provider call is still held.
            from concurrent.futures import wait, FIRST_COMPLETED
            done, _ = wait(futures, timeout=10, return_when=FIRST_COMPLETED)
            try:
                assert len(done) == 1
            finally:
                release_provider.set()
            results = [f.result(timeout=20) for f in futures]
        assert send.call_count == 1
    assert sorted(result[0] for result in results) == [200, 201]
    assert len({result[1] for result in results}) == 1
    assert Payment.objects.filter(order=order).count() == 1


def test_simultaneous_provider_updates_cannot_reverse_terminal_payment():
    user = get_user_model().objects.create_user(username='result@example.com', email='result@example.com', password='pass')
    order = Order.objects.create(user=user, province='Lusaka', town='Lusaka', street_address='Test', phone='0971111111', delivery_method='test', payment_method='mtn_momo', grand_total=Decimal('10'))
    payment = Payment.objects.create(order=order, user=user, method='mtn_momo', amount=Decimal('10'), idempotency_key='test-race')
    barrier = Barrier(2)
    def apply(state):
        return apply_provider_result(payment.id, {'reference': 'test-race', 'currency': 'ZMW', 'amount': '10', 'status': state})
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(invoke, lambda state=state: apply(state), barrier) for state in ('successful', 'failed')]
        assert all(f.result(timeout=20) for f in futures)
    payment.refresh_from_db(); order.refresh_from_db()
    assert (payment.status, order.status) in [('success', 'paid'), ('failed', 'awaiting_payment')]
