from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from apps.categories.models import Category
from apps.products.models import Product


class CatalogFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        category = Category.objects.create(name='Hair Care', slug='hair-care')
        other = Category.objects.create(name='Oils', slug='oils')
        for title, price, stock, cat in [('Shampoo', '50', 3, category), ('Conditioner', '200', 0, category), ('Oil', '100', 4, other)]:
            Product.objects.create(title=title, slug=title.lower(), description='', category=cat, price=Decimal(price), stock=stock)

    def test_filters_compose_with_search_and_sort(self):
        response = self.client.get('/api/products/', {'category__slug': 'hair-care', 'min_price': '40', 'max_price': '150', 'in_stock': 'true', 'search': 'shampoo', 'ordering': '-price'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p['title'] for p in response.data['results']], ['Shampoo'])

    def test_price_stock_sort_and_invalid_input(self):
        response = self.client.get('/api/products/', {'min_price': '50', 'max_price': '200', 'in_stock': 'true', 'ordering': '-price'})
        self.assertEqual([p['title'] for p in response.data['results']], ['Oil', 'Shampoo'])
        self.assertEqual(self.client.get('/api/products/', {'min_price': '-1'}).status_code, 400)
        self.assertEqual(self.client.get('/api/products/', {'max_price': 'invalid'}).status_code, 400)

    def test_price_filter_and_sort_use_discounted_price(self):
        Product.objects.filter(slug='oil').update(discount_percent=Decimal('60'))
        response = self.client.get('/api/products/', {'max_price': '45', 'ordering': 'price'})
        self.assertEqual([p['title'] for p in response.data['results']], ['Oil'])
        response = self.client.get('/api/products/', {'in_stock': 'true', 'ordering': 'price'})
        self.assertEqual([p['title'] for p in response.data['results']], ['Oil', 'Shampoo'])

    def test_storewide_discount_applies_to_price_filter(self):
        from apps.products.models import StoreDiscount
        StoreDiscount.objects.create(pk=1, percent=Decimal('25'))
        response = self.client.get('/api/products/', {'max_price': '40'})
        self.assertEqual([p['title'] for p in response.data['results']], ['Shampoo'])
