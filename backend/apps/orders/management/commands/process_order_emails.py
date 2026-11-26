from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.orders.email_notifications import process_one
from apps.orders.models import OrderEmail
from apps.users.password_reset import process_password_reset_email
from apps.users.support import process_support_inquiry_email
from apps.users.verification import process_verification_email


class Command(BaseCommand):
    help = 'Send due order email notifications through Resend.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100)
        parser.add_argument('--retry-reviewed', type=int)
        parser.add_argument('--confirm-provider-checked', action='store_true')

    def handle(self, *args, **options):
        if options['retry_reviewed']:
            if not options['confirm_provider_checked']:
                raise CommandError('Check Resend first, then add --confirm-provider-checked.')
            updated = OrderEmail.objects.filter(pk=options['retry_reviewed'], status='needs_review').update(
                status='pending', first_attempt_at=None, next_attempt_at=None, lease_until=None, last_error=''
            )
            if not updated:
                raise CommandError('No needs_review notification has that ID.')
        if not settings.RESEND_API_KEY:
            raise CommandError('RESEND_API_KEY is not configured; notifications remain queued.')
        count = 0
        while count < max(0, options['limit']) and process_verification_email():
            count += 1
        while count < max(0, options['limit']) and process_password_reset_email():
            count += 1
        while count < max(0, options['limit']) and process_support_inquiry_email():
            count += 1
        while count < max(0, options['limit']) and process_one():
            count += 1
        self.stdout.write(f'Processed {count} email notification(s).')
