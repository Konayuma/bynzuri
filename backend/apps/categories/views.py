from rest_framework import viewsets
from django.db import models
from django.db.models import Count
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=models.Q(products__is_active=True))
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None
