import logging
import uuid
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from apps.categories.models import Category

logger = logging.getLogger(__name__)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='products'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at'], name='products_active_created_idx'),
            models.Index(fields=['price'], name='products_price_idx'),
            models.Index(fields=['-rating'], name='products_rating_idx'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return f"Image for {self.product.title}"


@receiver(pre_save, sender=ProductImage)
def optimize_product_image(sender, instance, **kwargs):
    if kwargs.get('raw') or not instance.image:
        return
    # Skip already-committed files so metadata-only updates (alt_text, sort_order, etc.)
    # do not repeatedly re-encode existing images.
    if getattr(instance.image, '_committed', True):
        return
    from apps.products.signals import optimize_image
    try:
        optimized, filename = optimize_image(instance.image)
        instance.image.save(filename, optimized, save=False)
    except Exception as exc:
        logger.warning(
            'Failed to optimize product image for product %s: %s',
            instance.product_id,
            exc,
            exc_info=True,
        )
