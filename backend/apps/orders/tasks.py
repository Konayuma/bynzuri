from celery import shared_task
from django.core.management import call_command


@shared_task
def expire_unpaid_orders():
    call_command('expire_unpaid_orders')
