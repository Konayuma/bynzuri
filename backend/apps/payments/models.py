import uuid
from django.db import models
from django.conf import settings


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    METHOD_CHOICES = [
        ('mtn_momo', 'MTN MoMo'),
        ('airtel_money', 'Airtel Money'),
        ('zamtel_money', 'Zamtel Money'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
    ]

    OPERATOR_CHOICES = [
        ('mtn', 'MTN'),
        ('airtel', 'Airtel'),
        ('zamtel', 'Zamtel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name='payments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ZMW')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending'
    )
    transaction_reference = models.CharField(max_length=100, blank=True)
    lenco_reference = models.CharField(max_length=100, blank=True)
    lenco_id = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=64, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    gateway_response = models.JSONField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'

    def __str__(self):
        return f"{self.method} - {self.status} - {self.amount}"
