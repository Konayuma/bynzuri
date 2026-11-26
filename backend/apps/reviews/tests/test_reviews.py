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

@pytest.mark.django_db
def test_review_changes_require_owner_and_refresh_rating(user, product):
    from django.contrib.auth import get_user_model
    from rest_framework.test import APIClient
    owner = user
    other = get_user_model().objects.create_user(username='other@example.com', email='other@example.com', password='password123')
    review = Review.objects.create(product=product, user=owner, rating=5, comment='Good', is_approved=True)
    product.rating = 5; product.review_count = 1; product.save()
    client = APIClient(); client.force_authenticate(other)
    assert client.patch(f'/api/reviews/{review.id}/', {'rating': 1}, format='json').status_code == 403
    assert client.delete(f'/api/reviews/{review.id}/').status_code == 403
    client.force_authenticate(owner)
    assert client.patch(f'/api/reviews/{review.id}/', {'rating': 3}, format='json').status_code == 200
    review.refresh_from_db(); product.refresh_from_db()
    assert not review.is_approved and product.review_count == 0
    assert client.delete(f'/api/reviews/{review.id}/').status_code == 204

@pytest.mark.django_db
def test_reply_is_public_only_on_approved_reviews_and_cannot_be_set_by_customer(user, product):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user)
    response = client.post('/api/reviews/', {
        'product_slug': product.slug, 'rating': 5, 'comment': 'Lovely product',
        'staff_reply': 'Forged response',
    }, format='json')
    assert response.status_code == 201
    review = Review.objects.get(pk=response.data['id'])
    assert review.staff_reply == ''
    review.staff_reply = 'Thank you for sharing.'
    review.save()
    client.force_authenticate(user=None)
    assert not client.get('/api/reviews/', {'product': product.slug}).data['results']
    review.is_approved = True
    review.save()
    assert client.get('/api/reviews/', {'product': product.slug}).data['results'][0]['staff_reply'] == 'Thank you for sharing.'

@pytest.mark.django_db
def test_mine_includes_pending_and_edit_clears_reply(user, product):
    from rest_framework.test import APIClient
    review = Review.objects.create(product=product, user=user, rating=5, comment='Great product', is_approved=True, staff_reply='Thank you')
    client = APIClient()
    client.force_authenticate(user)
    response = client.patch(f'/api/reviews/{review.pk}/', {'comment': 'Updated review'}, format='json')
    assert response.status_code == 200
    assert response.data['is_approved'] is False
    assert response.data['staff_reply'] == ''
    mine = client.get('/api/reviews/', {'product': product.slug, 'mine': '1'})
    assert mine.data['results'][0]['id'] == str(review.pk)
    client.force_authenticate(user=None)
    assert client.get('/api/reviews/', {'product': product.slug, 'mine': '1'}).data['results'] == []
