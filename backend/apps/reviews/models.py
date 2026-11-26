import uuid
from django.db import models
from django.conf import settings
from django.db import transaction
from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from apps.products.models import Product


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    staff_reply = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.title} - {self.rating}★"


@receiver([post_save, post_delete], sender=Review)
def update_product_review_stats(sender, instance, **kwargs):
    # Covers model saves/deletes from the API and Django admin moderation.
    with transaction.atomic():
        product = Product.objects.select_for_update().filter(pk=instance.product_id).first()
        if product is None:
            return
        stats = Review.objects.filter(product=product, is_approved=True).aggregate(avg=Avg('rating'), count=Count('id'))
        Product.objects.filter(pk=product.pk).update(rating=stats['avg'] or 0, review_count=stats['count'])
