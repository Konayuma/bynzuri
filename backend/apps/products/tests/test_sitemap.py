from xml.etree import ElementTree as ET

import pytest
from django.test import override_settings
from apps.categories.models import Category
from apps.products.models import Product


@pytest.mark.django_db
@override_settings(PUBLIC_SITE_URL='https://bynzuri.com', ALLOWED_HOSTS=['untrusted.example', 'testserver'])
def test_sitemap_lists_active_products_and_public_pages(client):
    category = Category.objects.create(name='Care', slug='care')
    Product.objects.create(category=category, title='Oil', slug='hair-oil', description='', price='10', is_active=True)
    Product.objects.create(category=category, title='Hidden', slug='hidden', description='', price='10', is_active=False)
    response = client.get('/api/sitemap/', HTTP_HOST='untrusted.example')
    assert response.status_code == 200
    assert response['Content-Type'].startswith('application/xml')
    root = ET.fromstring(response.content)
    urls = [element.text for element in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    assert urls == ['https://bynzuri.com/', 'https://bynzuri.com/catalog', 'https://bynzuri.com/help', 'https://bynzuri.com/product/hair-oil']
    assert client.post('/api/sitemap/').status_code == 405


@pytest.mark.django_db
@override_settings(PUBLIC_SITE_URL='https://www.bynzuri.com')
def test_sitemap_uses_configured_canonical_host(client):
    assert b'https://www.bynzuri.com/catalog' in client.get('/api/sitemap/').content
