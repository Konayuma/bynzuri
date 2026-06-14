import uuid
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    STATE_CHOICES = [
        ('main_menu', 'Main Menu'),
        ('browsing_categories', 'Browsing Categories'),
        ('browsing_products', 'Browsing Products'),
        ('viewing_product', 'Viewing Product'),
        ('adding_quantity', 'Adding Quantity'),
        ('viewing_cart', 'Viewing Cart'),
        ('checkout_province', 'Checkout - Province'),
        ('checkout_town', 'Checkout - Town'),
        ('checkout_address', 'Checkout - Address'),
        ('checkout_phone', 'Checkout - Phone'),
        ('checkout_delivery', 'Checkout - Delivery Method'),
        ('checkout_payment', 'Checkout - Payment Method'),
        ('checkout_confirm', 'Checkout - Confirm'),
        ('order_status', 'Order Status'),
        ('viewing_order', 'Viewing Order'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    state = models.CharField(max_length=30, choices=STATE_CHOICES, default='main_menu')
    state_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'whatsapp_conversations'

    def __str__(self):
        return f"{self.phone_number} - {self.state}"


class WhatsAppMessage(models.Model):
    DIRECTION_CHOICES = [
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ]

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='messages'
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='whatsapp_messages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='whatsapp_messages'
    )
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='queued')
    to_number = models.CharField(max_length=20, db_index=True)
    from_number = models.CharField(max_length=20, blank=True)
    body = models.TextField()
    message_type = models.CharField(max_length=20, default='text')
    wapi_message_id = models.CharField(max_length=100, blank=True, db_index=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'whatsapp_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.direction} - {self.to_number} - {self.status}"
