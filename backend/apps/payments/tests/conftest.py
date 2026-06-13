import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.products.models import Product
from apps.orders.models import Order, OrderItem

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='test@bynzuri.com',
        email='test@bynzuri.com', password='test123',
        first_name='Test', last_name='User'
    )


@pytest.fixture
def order(user):
    order = Order.objects.create(
        user=user,
        province='Lusaka',
        town='Lusaka',
        street_address='123 Main',
        phone='260977000000',
        delivery_method='courier',
        payment_method='mtn_momo',
        total_amount=Decimal('200.00'),
        delivery_fee=Decimal('35.00'),
        grand_total=Decimal('235.00')
    )
    return order
