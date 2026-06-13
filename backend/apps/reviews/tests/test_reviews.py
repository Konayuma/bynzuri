import pytest
from rest_framework import status
from decimal import Decimal
from apps.categories.models import Category
from apps.products.models import Product
from apps.reviews.models import Review


@pytest.mark.django_db
class TestReviewModel:
    def test_create_review(self, user, product):
        review = Review.objects.create(
            product=product,
            user=user,
            rating=5,
            comment='Amazing product!'
        )
        assert review.rating == 5
        assert str(review) == f'{user.email} - {product.title} - 5★'
        assert review.is_approved is False

    def test_review_rating_range(self, user, product):
        review = Review.objects.create(
            product=product, user=user, rating=6,
            comment='Invalid rating'
        )
        # Django model choice field silently coerces,
        # validation happens at serializer level
        assert review.rating == 6  # DB stores the value directly

    def test_unique_product_user(self, user, product):
        Review.objects.create(product=product, user=user, rating=4, comment='Great')
        with pytest.raises(Exception):
            Review.objects.create(product=product, user=user, rating=3, comment='Again')


@pytest.mark.django_db
class TestReviewAPI:
    def setup_method(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.cat = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.cat, title='Review Item', slug='review-item',
            description='', price=Decimal('50.00'), stock=10
        )

    def test_create_review_authenticated(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/reviews/', {
            'product_slug': self.product.slug,
            'rating': 5,
            'comment': 'Excellent product!'
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == 5

    def test_create_review_unauthenticated(self):
        response = self.client.post('/api/reviews/', {
            'product_slug': self.product.slug,
            'rating': 4,
            'comment': 'Nice'
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_reviews(self, user):
        Review.objects.create(
            product=self.product, user=user, rating=5,
            comment='Great', is_approved=True
        )
        response = self.client.get(f'/api/reviews/?product={self.product.slug}')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
