from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'category', 'price', 'stock', 'is_active', 'is_featured', 'rating']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['title', 'description']
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'sort_order']
