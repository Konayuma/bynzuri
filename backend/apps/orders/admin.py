from django.contrib import admin
from .models import Order, OrderEmail, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'product_title', 'quantity', 'price_at_purchase']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'grand_total', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_method']
    search_fields = ['id', 'user__email', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['id', 'idempotency_key', 'total_amount', 'delivery_fee', 'grand_total', 'created_at']


@admin.register(OrderEmail)
class OrderEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'event', 'status', 'attempts', 'created_at', 'updated_at']
    list_filter = ['event', 'status']
    readonly_fields = [field.name for field in OrderEmail._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
