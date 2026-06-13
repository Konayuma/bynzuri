import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='test@bynzuri.com',
        email='test@bynzuri.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
        phone='260977000000'
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin@bynzuri.com',
        email='admin@bynzuri.com',
        password='admin123'
    )


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def auth_client(user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
