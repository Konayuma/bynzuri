import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import status
from apps.categories.models import Category
from apps.products.models import Product
from apps.orders.models import Order, OrderItem
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestDashboardAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.url = '/api/dashboard/'
        self.admin = User.objects.create_superuser(username='admin', email='admin@test.com', password='testpass123')
        self.user = User.objects.create_user(username='user1', email='user@test.com', password='testpass123')

    def test_dashboard_requires_admin(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_dashboard_admin_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_stats_empty(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        data = response.data
        assert data['revenue'] == 0
        assert data['orders'] == 0
        assert data['products'] == 0
        assert data['customers'] >= 0

    def test_dashboard_revenue(self):
        self.client.force_authenticate(user=self.admin)
        cat = Category.objects.create(name='Oils', slug='oils')
        product = Product.objects.create(
            category=cat, title='Oil', slug='oil-dash',
            description='Test', price=Decimal('100.00'), stock=10
        )
        Order.objects.create(
            user=self.user,
            idempotency_key='key1',
            total_amount=Decimal('200.00'),
            delivery_fee=Decimal('35.00'),
            grand_total=Decimal('235.00'),
            province='Lusaka',
            town='Lusaka',
            street_address='123 Main St',
            phone='260977777777',
            delivery_method='courier',
            payment_method='mtn_momo',
            status='paid'
        )
        response = self.client.get(self.url)
        assert float(response.data['revenue']) == 235.00
        assert response.data['orders'] == 1

    def test_sales_history_counts_only_eligible_orders_and_fills_missing_days(self):
        self.client.force_authenticate(user=self.admin)
        common = dict(user=self.user, total_amount=Decimal('100.00'), delivery_fee=Decimal('10.00'),
                      grand_total=Decimal('110.00'), province='Lusaka', town='Lusaka',
                      street_address='123', phone='260977777777', delivery_method='courier', payment_method='mtn_momo')
        paid = Order.objects.create(status='paid', **common)
        Order.objects.create(status='awaiting_payment', **common)
        Order.objects.create(status='cancelled', **common)
        OrderItem.objects.create(order=paid, product_title='Botanical oil', quantity=2, price_at_purchase=Decimal('50.00'))
        data = self.client.get(self.url, {'days': 7}).data
        assert len(data['sales_history']) == 7
        assert data['sales_history'][-1]['date'] == timezone.localdate().isoformat()
        assert data['sales_history'][-1]['orders'] == 1
        assert data['period_revenue'] == Decimal('110.00')
        assert data['period_orders'] == 1
        assert data['top_products'][0]['units'] == 2
        assert data['top_products'][0]['revenue'] == Decimal('100.00')
        assert self.client.get(self.url, {'days': 999}).status_code == 400

    def test_dashboard_low_stock(self):
        self.client.force_authenticate(user=self.admin)
        cat = Category.objects.create(name='Test', slug='test')
        Product.objects.create(
            category=cat, title='Low Stock', slug='low-stock',
            description='Test', price=Decimal('50.00'), stock=3
        )
        Product.objects.create(
            category=cat, title='High Stock', slug='high-stock',
            description='Test', price=Decimal('50.00'), stock=50
        )
        response = self.client.get(self.url)
        low_stock = list(response.data['low_stock'])
        assert len(low_stock) == 1
        assert low_stock[0]['title'] == 'Low Stock'

    def test_dashboard_recent_orders(self):
        self.client.force_authenticate(user=self.admin)
        cat = Category.objects.create(name='Test', slug='test')
        product = Product.objects.create(
            category=cat, title='Product', slug='product-dash',
            description='Test', price=Decimal('50.00'), stock=10
        )
        for i in range(3):
            Order.objects.create(
                user=self.user,
                idempotency_key=f'key{i}',
                total_amount=Decimal('50.00'),
                delivery_fee=Decimal('0'),
                grand_total=Decimal('50.00'),
                province='Lusaka',
                town='Lusaka',
                street_address='123 Main St',
                phone='260977777777',
                delivery_method='pickup',
                payment_method='mtn_momo',
                status='paid'
            )
        response = self.client.get(self.url)
        assert len(response.data['recent_orders']) == 3
