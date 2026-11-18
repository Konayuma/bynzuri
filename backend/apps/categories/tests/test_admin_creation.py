from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User
from apps.categories.models import Category


class CategoryCreationTest(TestCase):
    def test_staff_can_create_and_use_category(self):
        client = APIClient()
        self.assertIn(client.post('/api/categories/', {'name': 'Hair Care'}).status_code, (401, 403))
        customer = User.objects.create_user(username='customer', email='customer@example.com', password='password')
        client.force_authenticate(customer)
        self.assertEqual(client.post('/api/categories/', {'name': 'Hair Care'}).status_code, 403)
        admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        client.force_authenticate(admin)
        response = client.post('/api/categories/', {'name': 'Hair Care'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['slug'], 'hair-care')
        duplicate = client.post('/api/categories/', {'name': 'Hair Care'}, format='json')
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn('name', duplicate.data)
        product = client.post('/api/products/', {'title': 'Growth Elixir', 'category': response.data['id'], 'price': '185.00', 'stock': 1, 'slug': '', 'description': ''}, format='json')
        self.assertEqual(product.status_code, 201, product.data)
        self.assertEqual(product.data['slug'], 'growth-elixir')
        self.assertEqual(Category.objects.count(), 1)
