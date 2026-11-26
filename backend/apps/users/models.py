import uuid
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'customer')
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[('customer', 'Customer'), ('admin', 'Admin')],
        default='customer'
    )
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    nonce = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    sent_requested_at = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending', db_index=True)
    send_attempts = models.PositiveIntegerField(default=0)
    first_attempt_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    provider_id = models.CharField(max_length=255, blank=True)
    last_error = models.CharField(max_length=200, blank=True)


class PasswordResetRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_request')
    nonce = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    sent_requested_at = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending', db_index=True)
    send_attempts = models.PositiveIntegerField(default=0)
    first_attempt_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    provider_id = models.CharField(max_length=255, blank=True)
    last_error = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Password reset for {self.user.email} ({self.status})"


class SupportInquiry(models.Model):
    TOPIC_CHOICES = [
        ('order', 'Order & Delivery'),
        ('payment', 'Payments & Refunds'),
        ('product', 'Product Advice'),
        ('account', 'Account & Password'),
        ('returns', 'Returns & Exchanges'),
        ('general', 'General Inquiry'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_inquiries')
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    topic = models.CharField(max_length=40, choices=TOPIC_CHOICES, default='general')
    order_reference = models.CharField(max_length=64, blank=True)
    subject = models.CharField(max_length=160)
    message = models.TextField(max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', db_index=True)
    send_attempts = models.PositiveIntegerField(default=0)
    first_attempt_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)
    lease_until = models.DateTimeField(null=True, blank=True)
    provider_id = models.CharField(max_length=255, blank=True)
    last_error = models.CharField(max_length=200, blank=True)

    @property
    def reference(self):
        return f"SUP-{str(self.id).split('-')[0].upper()}"

    def __str__(self):
        return f"{self.reference} — {self.subject} ({self.email})"

    class Meta:
        db_table = 'support_inquiries'
        ordering = ['-created_at']
        verbose_name = 'Support inquiry'
        verbose_name_plural = 'Support inquiries'


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    province = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    street_address = models.TextField()
    phone = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street_address}, {self.town}, {self.province}"

    class Meta:
        db_table = 'addresses'
