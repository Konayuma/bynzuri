import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.products.models import Product

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='test@bynzuri.com',
        email='test@bynzuri.com', password='test123',
        first_name='Test', last_name='User'
    )


@pytest.fixture
def product():
    cat = Category.objects.create(name='Test Cat', slug='test-cat')
    return Product.objects.create(
        category=cat, title='Review Product', slug='review-product',
        description='Test', price=Decimal('99.99'), stock=10
    )
