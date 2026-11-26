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

    def test_register_accepts_international_phone_and_rejects_invalid_format(self):
        response = self.client.post(self.register_url, {'email': 'international@example.com', 'password': 'strongpass123', 'phone': '+12025550123'}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.get(email='international@example.com').phone == '+12025550123'
        response = self.client.post(self.register_url, {'email': 'invalid@example.com', 'password': 'strongpass123', 'phone': '+abc'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        User.objects.create_user(username='login@bynzuri.com', email='login@bynzuri.com', password='correctpass')
        response = self.client.post(self.token_url, {
            'email': 'login@bynzuri.com',
            'password': 'correctpass'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' not in response.data
        assert response.cookies['bynzuri_refresh']['httponly']

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

@pytest.mark.django_db
def test_cookie_session_csrf_rotation_and_logout():
    from rest_framework.test import APIClient
    user = User.objects.create_user(username='cookie@example.com', email='cookie@example.com', password='password123')
    client = APIClient(enforce_csrf_checks=True)
    assert client.post('/api/auth/token/', {'email': user.email, 'password': 'password123'}, format='json').status_code == 403
    csrf = client.get('/api/auth/csrf/').data['csrfToken']
    login = client.post('/api/auth/token/', {'email': user.email, 'password': 'password123'}, format='json', HTTP_X_CSRFTOKEN=csrf)
    assert login.status_code == 200 and 'refresh' not in login.data
    old_refresh = client.cookies['bynzuri_refresh'].value
    assert login.cookies['bynzuri_refresh']['httponly']
    assert client.post('/api/auth/token/refresh/', {}, format='json').status_code == 403
    refreshed = client.post('/api/auth/token/refresh/', {}, format='json', HTTP_X_CSRFTOKEN=csrf)
    assert refreshed.status_code == 200 and 'access' in refreshed.data and 'refresh' not in refreshed.data
    assert client.cookies['bynzuri_refresh'].value != old_refresh
    rotated_refresh = client.cookies['bynzuri_refresh'].value
    client.cookies['bynzuri_refresh'] = old_refresh
    assert client.post('/api/auth/token/refresh/', {}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code == 401
    client.cookies['bynzuri_refresh'] = rotated_refresh
    assert client.post('/api/auth/logout/', {}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code == 204
    assert client.post('/api/auth/token/refresh/', {}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code == 401
    client.cookies['bynzuri_refresh'] = rotated_refresh
    assert client.post('/api/auth/token/refresh/', {}, format='json', HTTP_X_CSRFTOKEN=csrf).status_code == 401

@pytest.mark.django_db
def test_cross_site_session_cookies_and_origin_checks(settings):
    from rest_framework.test import APIClient
    settings.SESSION_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SECURE = True
    settings.CSRF_COOKIE_SAMESITE = 'None'
    settings.CSRF_TRUSTED_ORIGINS = ['https://shop.example']
    User.objects.create_user(username='secure@example.com', email='secure@example.com', password='password123')
    client = APIClient(enforce_csrf_checks=True)
    token = client.get('/api/auth/csrf/', secure=True).data['csrfToken']
    data = {'email': 'secure@example.com', 'password': 'password123'}
    assert client.post('/api/auth/token/', data, format='json', secure=True, HTTP_ORIGIN='https://evil.example', HTTP_X_CSRFTOKEN=token).status_code == 403
    response = client.post('/api/auth/token/', data, format='json', secure=True, HTTP_ORIGIN='https://shop.example', HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200
    cookie = response.cookies['bynzuri_refresh']
    assert cookie['httponly'] and cookie['secure'] and cookie['samesite'] == 'None'
