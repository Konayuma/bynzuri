from django.contrib import admin
from .models import Province, Town, DeliveryMethod


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order']


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    list_filter = ['province']
    search_fields = ['name']


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'estimated_days', 'is_active']
    list_editable = ['price', 'is_active']
