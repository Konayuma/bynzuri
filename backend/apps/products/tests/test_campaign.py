from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient
from apps.products.models import Product, SaleCampaign


@pytest.mark.django_db
def test_campaign_is_scheduled_and_does_not_stack():
    SaleCampaign.objects.update_or_create(pk=1, defaults={
        'title': 'Black Friday sale', 'percent': 30, 'starts_on': date(2026, 11, 26),
        'ends_on': date(2026, 11, 28), 'fulfilment': 'Orders fulfilled 3rd December', 'enabled': True,
    })
    product = Product.objects.create(title='Serum', slug='serum', description='', price=Decimal('100'), discount_percent=Decimal('10'))
    client = APIClient()
    with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 25)):
        assert Decimal(str(client.get('/api/products/serum/').data['sale_price'])) == Decimal('90')
        assert client.get('/api/products/campaign/').data['title'] == 'Black Friday sale'
    with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 26)):
        assert Decimal(str(client.get('/api/products/serum/').data['sale_price'])) == Decimal('70')
        assert client.get('/api/products/', {'max_price': 70}).data['count'] == 1
    with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 29)):
        assert Decimal(str(client.get('/api/products/serum/').data['sale_price'])) == Decimal('90')
        assert client.get('/api/products/campaign/').data is None
    product.refresh_from_db()
    assert product.discount_percent == Decimal('10')


@pytest.mark.django_db
def test_campaign_edits_require_staff(django_user_model):
    client = APIClient()
    user = django_user_model.objects.create_user(username='campaign-user', email='campaign@example.com', password='test')
    client.force_authenticate(user=user)
    data = {'title': 'Sale', 'percent': '30', 'starts_on': '2026-11-26', 'ends_on': '2026-11-28', 'fulfilment': 'December', 'enabled': True}
    assert client.put('/api/products/campaign/', data, format='json').status_code == 403
    user.is_staff = True; user.save()
    data['ends_on'] = '2026-11-25'
    assert client.put('/api/products/campaign/', data, format='json').status_code == 400
    data['ends_on'] = '2026-11-28'
    assert client.put('/api/products/campaign/', data, format='json').status_code == 200
