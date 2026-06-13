import pytest
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product


@pytest.fixture
def category():
    return Category.objects.create(name='Hair Care', slug='hair-care')


@pytest.fixture
def product(category):
    return Product.objects.create(
        category=category,
        title='Growth Oil',
        slug='growth-oil',
        description='Premium hair growth oil with natural ingredients',
        price=Decimal('149.99'),
        stock=50
    )
