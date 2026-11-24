import pytest
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product
from apps.cart.models import Cart, CartItem


@pytest.mark.django_db
class TestCartAPI:
    def setup_method(self):
        self.client = APIClient()
        self.cat = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.cat, title='Item', slug='item',
            description='', price=Decimal('50.00'), stock=10
        )

    def test_get_cart_authenticated(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/cart/')
        assert response.status_code == status.HTTP_200_OK
        assert 'items' in response.data

    def test_add_to_cart(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/cart/add/', {
            'product': str(self.product.id),
            'quantity': 2
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data['items']) == 1

    def test_add_to_cart_increases_quantity(self, user):
        self.client.force_authenticate(user=user)
        self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 1}, format='json')
        response = self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 3}, format='json')
        assert response.data['items'][0]['quantity'] == 4

    def test_update_cart_item(self, user):
        self.client.force_authenticate(user=user)
        self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 1}, format='json')
        cart = Cart.objects.get(user=user)
        item = cart.items.first()
        response = self.client.patch(
            f'/api/cart/items/{item.id}/',
            {'quantity': 5}, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['items'][0]['quantity'] == 5

    def test_remove_cart_item(self, user):
        self.client.force_authenticate(user=user)
        self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 1}, format='json')
        cart = Cart.objects.get(user=user)
        item = cart.items.first()
        response = self.client.delete(f'/api/cart/items/{item.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['items']) == 0

    def test_cart_unauthenticated(self):
        response = self.client.get('/api/cart/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_merge_cart(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/cart/merge/', {
            'items': [
                {'product': str(self.product.id), 'quantity': 3}
            ]
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['items'][0]['quantity'] == 3

    def test_stock_and_partial_merge(self, user):
        import uuid
        self.client.force_authenticate(user=user)
        assert self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 11}, format='json').status_code == 400
        response = self.client.post('/api/cart/merge/', {'items': [
            {'product': str(uuid.uuid4()), 'quantity': 1},
            {'product': 'not-a-uuid', 'quantity': 1},
            {'product': str(self.product.id), 'quantity': 2},
        ]}, format='json')
        assert response.status_code == 200
        assert len(response.data['skipped']) == 2
        assert response.data['items'][0]['quantity'] == 2
        item = CartItem.objects.get(cart__user=user, product=self.product)
        assert self.client.patch(f'/api/cart/items/{item.id}/', {'quantity': 11}, format='json').status_code == 400
        self.product.is_active = False; self.product.save()
        assert self.client.post('/api/cart/add/', {'product': str(self.product.id), 'quantity': 1}, format='json').status_code == 400
