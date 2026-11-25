"""Transactional order email outbox. Never send from payment request handlers."""
import logging
import uuid
from datetime import timedelta
from html import escape

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import OrderEmail

logger = logging.getLogger(__name__)


def enqueue_order_email(order, event, recipient, *, paid=False, payment_reference=''):
    if not recipient:
        logger.warning('Order %s email %s has no recipient', order.pk, event)
        return
    from apps.delivery.models import DeliveryMethod

    try:
        delivery_id = uuid.UUID(str(order.delivery_method))
    except (ValueError, TypeError, AttributeError):
        delivery_id = None
    delivery_name = (DeliveryMethod.objects.filter(pk=delivery_id).values_list('name', flat=True).first()
                     if delivery_id else None) or order.delivery_method
    items = [{'title': item.product_title, 'quantity': item.quantity,
              'unit_price': str(item.price_at_purchase)} for item in order.items.all()]
    payload = {
        'order_id': str(order.pk), 'name': order.user.first_name if order.user else '',
        'customer_email': order.user.email if order.user else '',
        'items': items, 'subtotal': str(order.total_amount), 'delivery_fee': str(order.delivery_fee),
        'total': str(order.grand_total), 'paid': paid,
        'phone': order.phone, 'address': order.street_address, 'town': order.town,
        'province': order.province, 'delivery_method': delivery_name,
        'payment_method': order.payment_method, 'payment_reference': payment_reference,
        'notes': order.notes,
    }
    OrderEmail.objects.get_or_create(order=order, event=event, defaults={
        'recipient': recipient, 'payload': payload,
    })


def queue_order_created(order):
    enqueue_order_email(order, 'order_received', order.user.email if order.user else '')
    enqueue_order_email(order, 'owner_order', settings.ORDER_NOTIFICATION_EMAIL)


def queue_payment_confirmed(order, payment):
    reference = payment.lenco_reference or payment.transaction_reference or payment.idempotency_key
    enqueue_order_email(order, 'payment_receipt', order.user.email if order.user else '', paid=True, payment_reference=reference)
    enqueue_order_email(order, 'owner_paid', settings.ORDER_NOTIFICATION_EMAIL, paid=True, payment_reference=reference)


def queue_status_update(order, status):
    if status in ('dispatched', 'delivered', 'cancelled'):
        enqueue_order_email(order, f'order_{status}', order.user.email if order.user else '', paid=status in ('dispatched', 'delivered'))


def email_content(record):
    p = record.payload
    ref = p['order_id']
    subjects = {
        'order_received': 'We received your order — payment pending',
        'owner_order': 'New order received — payment pending',
        'payment_receipt': 'Payment received — your receipt',
        'owner_paid': 'Order payment confirmed',
        'order_dispatched': 'Your order has been dispatched',
        'order_delivered': 'Your order has been delivered',
        'order_cancelled': 'Your order has been cancelled',
    }
    subject = f"By Nzuri: {subjects[record.event]} ({ref[:8]})"
    lines = [subjects[record.event], f'Order: {ref}', '']
    if record.event.startswith('owner_'):
        lines += [f"Customer: {p['name']} ({p['customer_email']})", f"Phone: {p['phone']}",
                  f"Address: {p['address']}, {p['town']}, {p['province']}",
                  f"Delivery: {p['delivery_method']}", f"Order notes: {p['notes'] or 'None'}", '']
    lines += [f"{item['quantity']} × {item['title']} — ZMW {item['unit_price']} each" for item in p['items']]
    lines += ['', f"Subtotal: ZMW {p['subtotal']}", f"Delivery: ZMW {p['delivery_fee']}",
              f"Total: ZMW {p['total']}", f"Payment method: {p['payment_method']}",
              f"Payment: {'Confirmed' if p['paid'] else 'Not confirmed'}"]
    if p['payment_reference']:
        lines.append(f"Payment reference: {p['payment_reference']}")
    lines += ['', 'Questions? Reply to this email.', 'HairSkin by Nzuri']
    text = '\n'.join(lines)
    html = '<div style="font-family:Arial,sans-serif;line-height:1.6;white-space:pre-wrap">' + escape(text) + '</div>'
    return subject, text, html


def process_one():
    """Claim a row briefly; network I/O happens after committing the lease."""
    if not settings.RESEND_API_KEY:
        return False
    now = timezone.now()
    with transaction.atomic():
        query = OrderEmail.objects.filter(Q(status='pending', next_attempt_at__isnull=True) |
            Q(status='pending', next_attempt_at__lte=now) | Q(status='sending', lease_until__lt=now))
        record = query.select_for_update(skip_locked=True).order_by('created_at').first()
        if not record:
            return False
        if record.first_attempt_at and now - record.first_attempt_at >= timedelta(hours=23):
            record.status = 'needs_review'
            record.last_error = 'Retry window expired; check the provider before resending.'
            record.save(update_fields=['status', 'last_error', 'updated_at'])
            return True
        record.status = 'sending'
        record.first_attempt_at = record.first_attempt_at or now
        record.attempts += 1
        record.lease_until = now + timedelta(minutes=3)
        record.save(update_fields=['status', 'first_attempt_at', 'attempts', 'lease_until', 'updated_at'])
        record_id, attempt = record.pk, record.attempts

    subject, text, html = email_content(record)
    body = {'from': settings.RESEND_FROM_EMAIL, 'to': [record.recipient],
            'reply_to': settings.RESEND_REPLY_TO, 'subject': subject, 'text': text, 'html': html}
    try:
        response = requests.post('https://api.resend.com/emails', json=body, timeout=20,
            headers={'Authorization': f'Bearer {settings.RESEND_API_KEY}',
                     'Idempotency-Key': f'order-email/{record_id}'})
        if response.ok:
            provider_id = response.json().get('id')
            if not provider_id:
                raise ValueError('Missing provider message ID')
            updates = {'status': 'sent', 'provider_id': str(provider_id), 'last_error': ''}
        else:
            try:
                error_name = response.json().get('name', '')
            except (ValueError, AttributeError):
                error_name = ''
            retry = response.status_code == 429 or response.status_code >= 500 or (
                response.status_code == 409 and error_name == 'concurrent_idempotent_requests'
            )
            # Avoid logging provider response bodies, which may contain personal data.
            updates = {'status': 'pending' if retry else 'needs_review',
                       'last_error': f'Resend returned HTTP {response.status_code}'}
    except (requests.RequestException, ValueError):
        updates = {'status': 'pending', 'last_error': 'Provider request failed or response was invalid.'}
    if updates['status'] == 'pending':
        updates['next_attempt_at'] = timezone.now() + timedelta(minutes=min(60, 2 ** min(attempt, 6)))
    updates['lease_until'] = None
    updates['updated_at'] = timezone.now()
    OrderEmail.objects.filter(pk=record_id, status='sending', attempts=attempt).update(**updates)
    return True
