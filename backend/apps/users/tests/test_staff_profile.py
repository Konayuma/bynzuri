from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User


class StaffProfileTest(TestCase):
    def test_staff_status_is_exposed_but_cannot_be_changed_by_user(self):
        user = User.objects.create_user(username='customer', email='customer@example.com', password='password')
        client = APIClient()
        client.force_authenticate(user)
        response = client.patch('/api/auth/profile/', {'is_staff': True, 'role': 'admin'}, format='json')
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, 'customer')
        self.assertFalse(response.data['is_staff'])
