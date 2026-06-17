import pytest
from rest_framework import status
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = Category.objects.create(name='Hair Care', slug='hair-care')
        assert cat.name == 'Hair Care'
        assert cat.slug == 'hair-care'

    def test_slug_unique(self):
        Category.objects.create(name='Hair Care', slug='hair-care')
        with pytest.raises(Exception):
            Category.objects.create(name='Hair Care 2', slug='hair-care')

    def test_product_count_annotation(self):
        cat = Category.objects.create(name='Oils', slug='oils')
        Product.objects.create(
            category=cat, title='Oil 1', slug='oil-1',
            description='Test', price=Decimal('50.00'), stock=10
        )
        Product.objects.create(
            category=cat, title='Oil 2', slug='oil-2',
            description='Test', price=Decimal('60.00'), stock=5
        )
        cat.refresh_from_db()
        assert cat.products.count() == 2

    def test_category_ordering(self):
        Category.objects.create(name='Z Category', slug='z-cat', sort_order=2)
        Category.objects.create(name='A Category', slug='a-cat', sort_order=1)
        cats = list(Category.objects.values_list('slug', flat=True))
        assert cats[0] == 'a-cat'
        assert cats[1] == 'z-cat'


@pytest.mark.django_db
class TestCategoryAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.url = '/api/categories/'
        self.category = Category.objects.create(name='Hair Care', slug='hair-care')

    def test_list_categories(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_retrieve_category(self):
        response = self.client.get(f'{self.url}hair-care/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Hair Care'

    def test_category_product_count(self):
        Product.objects.create(
            category=self.category, title='Oil', slug='oil-prod',
            description='Test', price=Decimal('50.00'), stock=5
        )
        response = self.client.get(f'{self.url}hair-care/')
        assert response.data['product_count'] == 1

    def test_create_category_admin(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='admin', email='admin@test.com', password='testpass123')
        self.client.force_authenticate(user=admin)
        response = self.client.post(self.url, {'name': 'New Cat', 'slug': 'new-cat'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_category_non_admin(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='user1', email='user@test.com', password='testpass123')
        self.client.force_authenticate(user=user)
        response = self.client.post(self.url, {'name': 'New Cat', 'slug': 'new-cat'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_category_admin(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='admin2', email='admin@test.com', password='testpass123')
        self.client.force_authenticate(user=admin)
        response = self.client.patch(f'{self.url}hair-care/', {'name': 'Hair Products'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Hair Products'

    def test_delete_category_admin(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='admin3', email='admin@test.com', password='testpass123')
        self.client.force_authenticate(user=admin)
        response = self.client.delete(f'{self.url}hair-care/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
