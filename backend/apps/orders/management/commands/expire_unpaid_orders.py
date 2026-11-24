from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.orders.models import Order
from apps.orders.services import OrderTransitionError, transition_order


class Command(BaseCommand):
    help = 'Cancel old unpaid orders with no pending or confirmed payment and release reserved stock.'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24)

    def handle(self, *args, **options):
        if options['hours'] < 1:
            raise CommandError('Expiry must be at least one hour.')
        cutoff = timezone.now() - timedelta(hours=options['hours'])
        ids = Order.objects.filter(status='awaiting_payment', created_at__lte=cutoff).values_list('id', flat=True).iterator()
        cancelled = skipped = 0
        for order_id in ids:
            try:
                transition_order(order_id, 'cancelled', expire_before=cutoff)
                cancelled += 1
            except (OrderTransitionError, Order.DoesNotExist):
                skipped += 1
        self.stdout.write(f'Cancelled {cancelled} unpaid orders; skipped {skipped} requiring reconciliation.')
