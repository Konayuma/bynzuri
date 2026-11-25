import pytest
import uuid
from rest_framework import status
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.products.models import Product
from apps.cart.models import Cart, CartItem
from apps.delivery.models import DeliveryMethod
from apps.orders.models import Order

User = get_user_model()


@pytest.mark.django_db
class TestOrderCreation:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.cat = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.cat, title='Test Item', slug='test-item',
            description='', price=Decimal('100.00'), stock=5
        )
        self.delivery = DeliveryMethod.objects.create(
            name='Courier', description='Fast', price=Decimal('35.00'),
            estimated_days='1-2 days'
        )

    def _setup_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        return cart

    def test_create_order_success(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)

        response = self.client.post('/api/orders/', {
            'province': 'Lusaka',
            'town': 'Lusaka',
            'street_address': '123 Main Road',
            'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo'
        }, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'awaiting_payment'
        assert response.data['payment_method'] == 'mtn_momo'

    def test_order_deducts_stock(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)

        self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka',
            'street_address': '123', 'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'airtel_money'
        }, format='json')

        self.product.refresh_from_db()
        assert self.product.stock == 3  # 5 - 2

    def test_discount_is_reflected_in_cart_and_order(self, user):
        self.product.discount_percent = Decimal('15.00')
        self.product.save()
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        cart = self.client.get('/api/cart/')
        assert Decimal(str(cart.data['subtotal'])) == Decimal('170.00')
        assert Decimal(str(cart.data['items'][0]['product']['sale_price'])) == Decimal('85.00')
        response = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka', 'street_address': '123',
            'phone': '260977000000', 'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo',
        }, format='json')
        assert response.status_code == 201
        order = Order.objects.get(pk=response.data['id'])
        assert order.total_amount == Decimal('170.00')
        assert order.items.get().price_at_purchase == Decimal('85.00')

    def test_storewide_discount_is_charged_at_checkout(self, user):
        from apps.products.models import StoreDiscount
        StoreDiscount.objects.create(pk=1, percent=Decimal('20.00'))
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        cart = self.client.get('/api/cart/')
        assert Decimal(str(cart.data['subtotal'])) == Decimal('160.00')
        response = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka', 'street_address': '123',
            'phone': '260977000000', 'delivery_method': str(self.delivery.id), 'payment_method': 'mtn_momo',
        }, format='json')
        assert response.status_code == 201
        order = Order.objects.get(pk=response.data['id'])
        assert order.total_amount == Decimal('160.00')
        assert order.items.get().price_at_purchase == Decimal('80.00')

    def test_scheduled_campaign_is_charged_at_checkout(self, user):
        from datetime import date
        from unittest.mock import patch
        from apps.products.models import SaleCampaign
        SaleCampaign.objects.update_or_create(pk=1, defaults={'title': 'Sale', 'percent': 30, 'starts_on': date(2026, 11, 26), 'ends_on': date(2026, 11, 28), 'fulfilment': 'December', 'enabled': True})
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 26)):
            assert Decimal(str(self.client.get('/api/cart/').data['subtotal'])) == Decimal('140.00')
            response = self.client.post('/api/orders/', {'province': 'Lusaka', 'town': 'Lusaka', 'street_address': '123', 'phone': '260977000000', 'delivery_method': str(self.delivery.id), 'payment_method': 'mtn_momo'}, format='json')
        assert response.status_code == 201
        assert Order.objects.get(pk=response.data['id']).items.get().price_at_purchase == Decimal('70.00')

    def test_order_with_insufficient_stock(self, user):
        self.client.force_authenticate(user=user)
        self.product.stock = 1
        self.product.save()
        self._setup_cart(user)  # cart has qty 2

        response = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka',
            'street_address': '123', 'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'visa'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        self.product.refresh_from_db()
        assert self.product.stock == 1  # not deducted

    def test_checkout_key_replays_same_order_and_allows_next_order(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        data = {
            'checkout_key': str(uuid.uuid4()),
            'province': 'Lusaka', 'town': 'Lusaka', 'street_address': '123',
            'phone': '260977000000', 'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo'
        }
        first = self.client.post('/api/orders/', data, format='json')
        replay = self.client.post('/api/orders/', data, format='json')
        assert first.status_code == 201
        assert replay.status_code == 200
        assert first.data['id'] == replay.data['id']
        self.product.refresh_from_db()
        assert self.product.stock == 3
        self._setup_cart(user)
        data['checkout_key'] = str(uuid.uuid4())
        second = self.client.post('/api/orders/', data, format='json')
        assert second.status_code == 201
        assert second.data['id'] != first.data['id']
        self.product.refresh_from_db()
        assert self.product.stock == 1

    def test_unavailable_delivery_does_not_deduct_stock(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        self.delivery.is_active = False
        self.delivery.save()
        response = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka', 'street_address': '123',
            'phone': '260977000000', 'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo'
        }, format='json')
        assert response.status_code == 400
        self.product.refresh_from_db()
        assert self.product.stock == 5

    def test_order_with_empty_cart(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka',
            'street_address': '123', 'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_order_list(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK

    def test_order_detail(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)
        create_resp = self.client.post('/api/orders/', {
            'province': 'Lusaka', 'town': 'Lusaka',
            'street_address': '123', 'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'mtn_momo'
        }, format='json')
        order_id = create_resp.data['id']

        response = self.client.get(f'/api/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order_id

    def test_cancel_restores_stock_once_and_rejects_invalid_transition(self, user):
        from apps.orders.services import transition_order, OrderTransitionError
        self.client.force_authenticate(user=user); self._setup_cart(user)
        response = self.client.post('/api/orders/', {'province':'Lusaka','town':'Lusaka','street_address':'123','phone':'260977000000','delivery_method':str(self.delivery.id),'payment_method':'mtn_momo'}, format='json')
        order_id = response.data['id']
        transition_order(order_id, 'cancelled'); transition_order(order_id, 'cancelled')
        self.product.refresh_from_db(); assert self.product.stock == 5
        with pytest.raises(OrderTransitionError): transition_order(order_id, 'awaiting_payment')

    def test_expiry_skips_pending_payment(self, user):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone
        from apps.payments.models import Payment
        self.client.force_authenticate(user=user); self._setup_cart(user)
        response = self.client.post('/api/orders/', {'province':'Lusaka','town':'Lusaka','street_address':'123','phone':'260977000000','delivery_method':str(self.delivery.id),'payment_method':'mtn_momo'}, format='json')
        order = Order.objects.get(id=response.data['id']); Order.objects.filter(id=order.id).update(created_at=timezone.now()-timedelta(hours=25))
        Payment.objects.create(order=order, user=user, method='mtn_momo', amount=order.grand_total, idempotency_key='pending-expiry')
        call_command('expire_unpaid_orders')
        order.refresh_from_db(); self.product.refresh_from_db()
        assert order.status == 'awaiting_payment' and self.product.stock == 3

    def test_expiry_releases_stock_only_once(self, user):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone
        self.client.force_authenticate(user=user); self._setup_cart(user)
        response = self.client.post('/api/orders/', {'province':'Lusaka','town':'Lusaka','street_address':'123','phone':'260977000000','delivery_method':str(self.delivery.id),'payment_method':'mtn_momo'}, format='json')
        order = Order.objects.get(id=response.data['id'])
        Order.objects.filter(pk=order.pk).update(created_at=timezone.now() - timedelta(hours=25))
        call_command('expire_unpaid_orders'); call_command('expire_unpaid_orders')
        order.refresh_from_db(); self.product.refresh_from_db()
        assert order.status == 'cancelled' and self.product.stock == 5

    def test_admin_invalid_pagination_is_not_server_error(self, user):
        user.is_staff = True; user.save(); self.client.force_authenticate(user=user)
        for page in ['abc', '0', '-1']:
            assert self.client.get('/api/orders/admin/', {'page': page}).status_code == 404
