import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.delivery.models import Province, Town
from apps.users.models import Address

pytestmark = pytest.mark.django_db


def test_saved_addresses_are_private_valid_and_return_names():
    User = get_user_model()
    owner = User.objects.create_user(username='owner', email='owner@example.com', password='password123')
    other = User.objects.create_user(username='other', email='other@example.com', password='password123')
    province = Province.objects.create(name='Lusaka', slug='lusaka')
    town = Town.objects.create(province=province, name='Lusaka', slug='lusaka')
    other_province = Province.objects.create(name='Copperbelt', slug='copperbelt')
    client = APIClient(); client.force_authenticate(user=owner)
    payload = {'province': str(province.pk), 'town': str(town.pk), 'street_address': '123 Main Road', 'phone': '0971234567', 'is_default': True}
    first = client.post('/api/auth/addresses/', payload, format='json')
    assert first.status_code == 201
    assert first.data['province_name'] == 'Lusaka' and first.data['town_name'] == 'Lusaka'
    payload['street_address'] = 'Second Road'
    assert client.post('/api/auth/addresses/', payload, format='json').status_code == 201
    assert Address.objects.filter(user=owner, is_default=True).count() == 1
    assert len(client.get('/api/auth/addresses/').data['results']) == 2
    assert client.post('/api/auth/addresses/', {**payload, 'province': str(other_province.pk)}, format='json').status_code == 400
    assert client.post('/api/auth/addresses/', {**payload, 'province': 'invalid'}, format='json').status_code == 400
    assert client.post('/api/auth/addresses/', {**payload, 'phone': '123'}, format='json').status_code == 400
    client.force_authenticate(user=other)
    assert client.get('/api/auth/addresses/').data['results'] == []
    assert client.get(f"/api/auth/addresses/{first.data['id']}/").status_code == 404
