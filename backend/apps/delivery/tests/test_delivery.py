import pytest
from rest_framework import status
from decimal import Decimal
from apps.delivery.models import Province, Town, DeliveryMethod


@pytest.mark.django_db
class TestDeliveryModels:
    def test_create_province(self):
        province = Province.objects.create(name='Lusaka', slug='lusaka')
        assert str(province) == 'Lusaka'
        assert province.slug == 'lusaka'

    def test_create_town(self, province):
        town = Town.objects.create(province=province, name='Lusaka City', slug='lusaka-city')
        assert str(town) == 'Lusaka City, Lusaka'
        assert town.province == province

    def test_town_unique_together(self, province):
        Town.objects.create(province=province, name='Town1', slug='town1')
        with pytest.raises(Exception):
            Town.objects.create(province=province, name='Town1', slug='town1')

    def test_delivery_method(self):
        dm = DeliveryMethod.objects.create(
            name='Express', description='Fast', price=Decimal('50.00'),
            estimated_days='1 day', sort_order=1
        )
        assert str(dm) == 'Express - K50.00'
        assert dm.is_active is True


@pytest.mark.django_db
class TestDeliveryAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.province = Province.objects.create(name='Lusaka', slug='lusaka')
        Town.objects.create(province=self.province, name='Lusaka', slug='lusaka')
        Town.objects.create(province=self.province, name='Chongwe', slug='chongwe')
        DeliveryMethod.objects.create(name='Courier', description='Fast',
                                       price=Decimal('35'), estimated_days='1-2 days')

    def test_list_provinces(self):
        response = self.client.get('/api/delivery/provinces/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_filter_towns_by_province(self):
        response = self.client.get(f'/api/delivery/towns/?province={self.province.id}')
        assert response.status_code == status.HTTP_200_OK
        names = [t['name'] for t in response.data]
        assert 'Lusaka' in names
        assert 'Chongwe' in names

    def test_list_delivery_methods(self):
        response = self.client.get('/api/delivery/methods/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
