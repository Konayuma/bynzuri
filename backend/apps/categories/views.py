from rest_framework import viewsets, permissions
from django.db import models
from django.db.models import Count
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(
        product_count=Count('products', filter=models.Q(products__is_active=True))
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
