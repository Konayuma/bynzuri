from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.products.models import Product


class SignatureCatalogTest(TestCase):
    def test_import_is_idempotent_and_preserves_existing_data(self):
        call_command('import_signature_catalog', stdout=StringIO())
        product = Product.objects.get(slug='growth-elixir')
        product.stock = 12
        product.price = '199.00'
        product.save()
        call_command('import_signature_catalog', stdout=StringIO())
        product.refresh_from_db()
        self.assertEqual(Product.objects.count(), 8)
        self.assertEqual(product.stock, 12)
        self.assertEqual(str(product.price), '199.00')

    def test_guest_can_browse_sections_search_and_view_detail(self):
        call_command('import_signature_catalog', stdout=StringIO())
        client = APIClient()
        hair = client.get('/api/products/', {'category__slug': 'hair-care'})
        self.assertEqual(hair.status_code, 200)
        self.assertEqual(hair.data['count'], 4)
        combined = client.get('/api/products/', {'category__slug': 'hair-care', 'search': 'conditioner'})
        self.assertEqual(combined.data['count'], 2)
        growth = client.get('/api/products/', {'category__slug': 'hair-growth'})
        self.assertEqual([p['slug'] for p in growth.data['results']], ['growth-elixir'])
        category_search = client.get('/api/products/', {'search': 'hair growth'})
        self.assertEqual(category_search.data['count'], 1)
        detail = client.get('/api/products/growth-elixir/')
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['category_slug'], 'hair-growth')

    def test_web_import_requires_staff_and_preserves_existing_products(self):
        from apps.users.models import User
        client = APIClient()
        self.assertIn(client.post('/api/products/import-signature/').status_code, (401, 403))
        customer = User.objects.create_user(username='customer', email='customer@example.com', password='secret')
        client.force_authenticate(customer)
        self.assertEqual(client.post('/api/products/import-signature/').status_code, 403)
        admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='secret')
        client.force_authenticate(admin)
        response = client.post('/api/products/import-signature/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['created']), 8)
        self.assertEqual(Product.objects.get(slug='growth-elixir').stock, 0)
        product = Product.objects.get(slug='growth-elixir')
        product.price = '199.00'
        product.save()
        response = client.post('/api/products/import-signature/')
        self.assertEqual(len(response.data['skipped']), 8)
        product.refresh_from_db()
        self.assertEqual(str(product.price), '199.00')
