from django.db import transaction
from django.db.models import F
from .models import Order
from apps.products.models import Product

ALLOWED_TRANSITIONS = {
    'awaiting_payment': {'cancelled'},
    'paid': {'processing'},
    'processing': {'dispatched'},
    'dispatched': {'delivered'},
    'delivered': set(),
    'cancelled': set(),
}


class OrderTransitionError(ValueError):
    pass


@transaction.atomic
def transition_order(order_id, new_status, *, expire_before=None):
    order = Order.objects.select_for_update().get(pk=order_id)
    if expire_before and (order.status != 'awaiting_payment' or order.created_at > expire_before):
        raise OrderTransitionError('Order is no longer eligible for expiry.')
    if order.status == new_status:
        return order
    if new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise OrderTransitionError('This order status transition is not allowed.')
    if new_status == 'cancelled':
        if order.payments.filter(status__in=['pending', 'processing', 'success']).exists():
            raise OrderTransitionError('Payment is pending or confirmed. Reconcile it before cancelling this order.')
        quantities = {}
        for item in order.items.exclude(product_id=None):
            quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
        for product_id in sorted(quantities, key=str):
            Product.objects.filter(pk=product_id).update(stock=F('stock') + quantities[product_id])
    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    return order
