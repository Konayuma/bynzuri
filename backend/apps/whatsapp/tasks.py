import logging
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_whatsapp_notification(self, to_number: str, message: str):
    from .services import MichoWAPIClient, MichoWAPIError
    from .models import WhatsAppMessage

    if not settings.MICHOWAPI_API_KEY:
        logger.warning('MICHOWAPI_API_KEY not set, skipping WhatsApp notification to %s', to_number)
        return

    msg_record = WhatsAppMessage.objects.create(
        direction='outbound',
        to_number=to_number,
        body=message,
    )

    try:
        client = MichoWAPIClient()
        result = client.send_text_message(to=to_number, message=message)
        msg_record.status = result.get('status', 'sent')
        msg_record.wapi_message_id = result.get('message_id', '')
        msg_record.save(update_fields=['status', 'wapi_message_id'])
        logger.info('WhatsApp notification sent to %s: %s', to_number, result.get('message_id'))
    except MichoWAPIError as exc:
        msg_record.status = 'failed'
        msg_record.error_message = str(exc)
        msg_record.save(update_fields=['status', 'error_message'])
        raise self.retry(exc=exc)
