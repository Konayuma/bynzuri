from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import models
from django.db.models import Avg
from django.shortcuts import get_object_or_404
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

    def create(self, request, *args, **kwargs):
        product_slug = request.data.get('product_slug')
        if not product_slug:
            return Response(
                {'detail': 'product_slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        product = get_object_or_404(Product, slug=product_slug)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user, product=product)
        self._update_product_rating(product)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def _update_product_rating(self, product):
        stats = Review.objects.filter(product=product, is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            count=models.Count('id')
        )
        product.rating = stats['avg_rating'] or 0
        product.review_count = stats['count'] or 0
        product.save()
