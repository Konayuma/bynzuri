from rest_framework import viewsets, permissions
from django.db import models
from django.db.models import Avg
from .models import Review
from apps.products.models import Product
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)
        product_slug = self.request.query_params.get('product')
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        return queryset

    def perform_create(self, serializer):
        product = Product.objects.get(slug=self.request.data.get('product_slug'))
        review = serializer.save(user=self.request.user, product=product)
        self._update_product_rating(product)

    def _update_product_rating(self, product):
        stats = Review.objects.filter(product=product, is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            count=models.Count('id')
        )
        product.rating = stats['avg_rating'] or 0
        product.review_count = stats['count'] or 0
        product.save()
