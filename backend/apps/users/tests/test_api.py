import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthAPI:
    def setup_method(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.token_url = '/api/auth/token/'
        self.profile_url = '/api/auth/profile/'

    def test_register_user(self):
        data = {
            'email': 'new@bynzuri.com',
            'password': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '260977000000'
        }
        response = self.client.post(self.register_url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'new@bynzuri.com'
        assert 'password' not in response.data

    def test_register_duplicate_email(self):
        User.objects.create_user(username='dup@bynzuri.com', email='dup@bynzuri.com', password='test123')
        data = {
            'email': 'dup@bynzuri.com',
            'password': 'strongpass123',
            'first_name': 'Dup',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        User.objects.create_user(username='login@bynzuri.com', email='login@bynzuri.com', password='correctpass')
        response = self.client.post(self.token_url, {
            'email': 'login@bynzuri.com',
            'password': 'correctpass'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_password(self):
        User.objects.create_user(username='login@bynzuri.com', email='login@bynzuri.com', password='correctpass')
        response = self.client.post(self.token_url, {
            'email': 'login@bynzuri.com',
            'password': 'wrongpass'
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_authenticated(self):
        user = User.objects.create_user(
            username='profile@bynzuri.com', email='profile@bynzuri.com', password='test123',
            first_name='Profile', last_name='Test'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'profile@bynzuri.com'
        assert response.data['first_name'] == 'Profile'

    def test_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
