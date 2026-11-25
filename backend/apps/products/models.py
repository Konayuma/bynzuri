import logging
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from apps.categories.models import Category

logger = logging.getLogger(__name__)


class StoreDiscount(models.Model):
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class SaleCampaign(models.Model):
    title = models.CharField(max_length=100, default='Black Friday sale')
    percent = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    starts_on = models.DateField()
    ends_on = models.DateField()
    fulfilment = models.CharField(max_length=160, default='Orders fulfilled 3rd December')
    enabled = models.BooleanField(default=True)


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
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
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

    @property
    def effective_discount_percent(self):
        storewide = getattr(self, 'store_discount', None)
        if storewide is None:
            storewide = StoreDiscount.objects.filter(pk=1).values_list('percent', flat=True).first() or Decimal('0')
            self.store_discount = storewide
        campaign = getattr(self, 'campaign_discount', None)
        if campaign is None:
            today = timezone.localdate()
            campaign = SaleCampaign.objects.filter(pk=1, enabled=True, starts_on__lte=today, ends_on__gte=today).values_list('percent', flat=True).first() or Decimal('0')
            self.campaign_discount = campaign
        return max(self.discount_percent, storewide, campaign)

    @property
    def sale_price(self):
        return (self.price * (Decimal('1') - self.effective_discount_percent / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


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
