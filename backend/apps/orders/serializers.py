from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'quantity', 'price_at_purchase']


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'delivery_fee',
            'grand_total', 'items', 'item_count',
            'province', 'town', 'payment_method',
            'created_at'
        ]

    def get_item_count(self, obj):
        return sum(item.quantity for item in obj.items.all())


class OrderCreateSerializer(serializers.Serializer):
    province = serializers.CharField(max_length=100)
    town = serializers.CharField(max_length=100)
    street_address = serializers.CharField()
    phone = serializers.CharField(max_length=20)
    delivery_method = serializers.CharField(max_length=50)
    payment_method = serializers.CharField(max_length=50)
    notes = serializers.CharField(required=False, allow_blank=True)
