import uuid
from django.db import models
from django.conf import settings
from apps.products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('awaiting_payment', 'Awaiting Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='awaiting_payment'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    province = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    street_address = models.TextField()
    phone = models.CharField(max_length=20)
    delivery_method = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at'], name='orders_status_created_idx'),
            models.Index(fields=['user', '-created_at'], name='orders_user_created_idx'),
        ]

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f"{self.quantity}x {self.product_title}"
