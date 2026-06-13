from django.contrib import admin
from django.db import models
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'sort_order', 'is_active', 'product_count']
    list_editable = ['sort_order', 'is_active']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=models.Count('products')
        )

    def product_count(self, obj):
        return obj.product_count
