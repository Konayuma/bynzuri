from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from apps.orders.models import Order
from .tasks import send_whatsapp_notification


@receiver(post_save, sender=Order)
def notify_order_status_change(sender, instance, created, **kwargs):
    if created:
        return

    if not instance.phone:
        return

    templates = {
        'paid': (
            'Payment Confirmed ✅\n\n'
            f'Your order #{instance.id} has been paid successfully!\n'
            f'Total: ZMW {instance.grand_total}\n'
            'We\'ll start processing it right away.'
        ),
        'processing': (
            'Order Processing 🔄\n\n'
            f'Your order #{instance.id} is now being processed.\n'
            'We\'ll notify you when it\'s been dispatched.'
        ),
        'dispatched': (
            'Order Dispatched 🚚\n\n'
            f'Your order #{instance.id} is on its way!\n'
            f'Delivery to: {instance.town}, {instance.province}\n'
            'Thank you for shopping with By Nzuri.'
        ),
        'delivered': (
            'Order Delivered ✅\n\n'
            f'Your order #{instance.id} has been delivered.\n'
            'We hope you love your items! Feel free to leave a review.'
        ),
        'cancelled': (
            'Order Cancelled ❌\n\n'
            f'Your order #{instance.id} has been cancelled.\n'
            'Contact us if you have any questions.'
        ),
    }

    message = templates.get(instance.status)
    if message:
        transaction.on_commit(
            lambda: send_whatsapp_notification.delay(to_number=instance.phone, message=message),
            robust=True,
        )
