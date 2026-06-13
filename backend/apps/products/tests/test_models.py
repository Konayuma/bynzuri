import pytest
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product, ProductImage


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self, category):
        product = Product.objects.create(
            category=category,
            title='Growth Oil',
            slug='growth-oil',
            description='Premium hair growth oil',
            price=Decimal('149.99'),
            stock=50
        )
        assert product.title == 'Growth Oil'
        assert product.price == Decimal('149.99')
        assert product.is_in_stock is True
        assert str(product) == 'Growth Oil'

    def test_out_of_stock(self, category):
        product = Product.objects.create(
            category=category, title='Sold Out', slug='sold-out',
            description='', price=Decimal('99.99'), stock=0
        )
        assert product.is_in_stock is False

    def test_low_stock(self, category):
        product = Product.objects.create(
            category=category, title='Low Stock', slug='low-stock',
            description='', price=Decimal('99.99'), stock=3
        )
        assert product.stock <= 5
        assert product.is_in_stock is True

    def test_product_defaults(self, category):
        product = Product.objects.create(
            category=category, title='Defaults', slug='defaults',
            description='Test', price=Decimal('50.00'), stock=10
        )
        assert product.is_active is True
        assert product.is_featured is False
        assert product.rating == Decimal('0')
        assert product.review_count == 0


@pytest.mark.django_db
class TestProductImageModel:
    def test_create_image(self, product):
        image = ProductImage.objects.create(
            product=product,
            image='products/test.jpg',
            alt_text='Test image',
            is_primary=True
        )
        assert image.product == product
        assert image.is_primary is True
        assert str(image) == f'Image for {product.title}'

    def test_image_ordering(self, product):
        img1 = ProductImage.objects.create(product=product, image='img1.jpg', sort_order=2)
        img2 = ProductImage.objects.create(product=product, image='img2.jpg', sort_order=1)
        images = product.images.all()
        assert images[0] == img2  # lower sort_order first
        assert images[1] == img1
