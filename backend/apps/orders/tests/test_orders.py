import pytest
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

    def test_idempotent_order(self, user):
        self.client.force_authenticate(user=user)
        self._setup_cart(user)

        data = {
            'province': 'Lusaka', 'town': 'Lusaka',
            'street_address': '123', 'phone': '260977000000',
            'delivery_method': str(self.delivery.id),
            'payment_method': 'mastercard'
        }
        self.client.post('/api/orders/', data, format='json')
        # Re-setup cart (previous order cleared it)
        self._setup_cart(user)
        response = self.client.post('/api/orders/', data, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT

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
