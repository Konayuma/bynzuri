import uuid
from django.db import models


class Province(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'provinces'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Town(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE,
        related_name='towns'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)

    class Meta:
        db_table = 'towns'
        unique_together = ['province', 'slug']
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.province.name}"


class DeliveryMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'delivery_methods'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} - K{self.price}"
