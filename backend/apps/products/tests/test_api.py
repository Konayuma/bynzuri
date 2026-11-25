import pytest
from rest_framework import status
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product


@pytest.mark.django_db
class TestProductAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.list_url = '/api/products/'
        self.category = Category.objects.create(name='Hair Care', slug='hair-care')
        self.product = Product.objects.create(
            category=self.category,
            title='Test Oil',
            slug='test-oil',
            description='Great oil',
            price=Decimal('99.99'),
            stock=20
        )

    def test_list_products(self):
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_list_products_pagination(self):
        for i in range(15):
            Product.objects.create(
                category=self.category,
                title=f'Product {i}',
                slug=f'product-{i}',
                description='Test',
                price=Decimal('50.00'),
                stock=10
            )
        response = self.client.get(self.list_url)
        assert len(response.data['results']) == 12
        assert response.data['count'] >= 16

    def test_filter_by_category(self):
        cat2 = Category.objects.create(name='Oils', slug='oils')
        Product.objects.create(category=cat2, title='Oil', slug='oil-product',
                                description='', price=Decimal('50.00'), stock=5)
        response = self.client.get(f'{self.list_url}?category__slug=hair-care')
        all_hair_care = all(
            p['category_name'] == 'Hair Care' for p in response.data['results']
        )
        assert all_hair_care is True

    def test_search_products(self):
        response = self.client.get(f'{self.list_url}?search=Test Oil')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_retrieve_product(self):
        response = self.client.get(f'{self.list_url}{self.product.slug}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Oil'
        assert response.data['price'] == '99.99'

    def test_only_staff_can_set_valid_discount(self, django_user_model):
        endpoint = f'{self.list_url}{self.product.slug}/'
        user = django_user_model.objects.create_user(username='discount-test', email='discount@example.com', password='test-password')
        self.client.force_authenticate(user=user)
        assert self.client.patch(endpoint, {'discount_percent': '20.00'}, format='json').status_code == 403
        user.is_staff = True
        user.save()
        assert self.client.patch(endpoint, {'discount_percent': '101'}, format='json').status_code == 400
        assert self.client.patch(endpoint, {'discount_percent': '20.00'}, format='json').status_code == 200
        response = self.client.get(endpoint)
        assert Decimal(str(response.data['sale_price'])) == Decimal('79.99')

    def test_storewide_discount_permissions_and_precedence(self, django_user_model):
        user = django_user_model.objects.create_user(username='store-test', email='store@example.com', password='test-password')
        self.client.force_authenticate(user=user)
        endpoint = '/api/products/store-discount/'
        assert self.client.put(endpoint, {'percent': '25'}, format='json').status_code == 403
        user.is_staff = True
        user.save()
        assert self.client.put(endpoint, {'percent': '101'}, format='json').status_code == 400
        assert self.client.put(endpoint, {'percent': '25'}, format='json').status_code == 200
        item = self.client.get(f'{self.list_url}{self.product.slug}/').data
        assert Decimal(str(item['effective_discount_percent'])) == Decimal('25')
        assert Decimal(str(item['sale_price'])) == Decimal('74.99')
        self.product.discount_percent = Decimal('30')
        self.product.save()
        item = self.client.get(f'{self.list_url}{self.product.slug}/').data
        assert Decimal(str(item['sale_price'])) == Decimal('69.99')
        assert self.client.put(endpoint, {'percent': '0'}, format='json').status_code == 200
        assert Decimal(str(self.client.get(f'{self.list_url}{self.product.slug}/').data['sale_price'])) == Decimal('69.99')

    def test_best_sellers(self):
        response = self.client.get(f'{self.list_url}best-sellers/')
        assert response.status_code == status.HTTP_200_OK

    def test_new_arrivals(self):
        response = self.client.get(f'{self.list_url}new-arrivals/')
        assert response.status_code == status.HTTP_200_OK
