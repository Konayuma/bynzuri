import logging
from rest_framework import views, status, permissions
from rest_framework.response import Response

from .models import WhatsAppMessage
from .serializers import (
    WhatsAppMessageSerializer,
    SendTextSerializer,
    WebhookSerializer,
)
from .services import MichoWAPIClient, MichoWAPIError
from .bot import process_message

logger = logging.getLogger(__name__)


class SendMessageView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SendTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to = serializer.validated_data['to']
        message = serializer.validated_data['message']

        client = MichoWAPIClient()

        whatsapp_message = WhatsAppMessage.objects.create(
            user=request.user if request.user.is_authenticated else None,
            direction='outbound',
            status='queued',
            to_number=to,
            body=message,
        )

        try:
            result = client.send_text_message(to=to, message=message)
            whatsapp_message.status = result.get('status', 'sent')
            whatsapp_message.wapi_message_id = result.get('message_id', '')
            whatsapp_message.save(update_fields=['status', 'wapi_message_id'])
        except MichoWAPIError as e:
            whatsapp_message.status = 'failed'
            whatsapp_message.error_message = str(e)
            whatsapp_message.save(update_fields=['status', 'error_message'])
            return Response(
                {'detail': 'Failed to send message', 'error': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        output = WhatsAppMessageSerializer(whatsapp_message).data
        return Response(output, status=status.HTTP_201_CREATED)


class MessageHistoryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chat_id = request.query_params.get('chat_id')
        from_me = request.query_params.get('from_me')
        msg_type = request.query_params.get('type')
        page = request.query_params.get('page', 1)

        client = MichoWAPIClient()
        params = {'page': page}
        if chat_id:
            params['chat_id'] = chat_id
        if from_me is not None:
            params['from_me'] = from_me
        if msg_type:
            params['type'] = msg_type

        try:
            result = client.get_message_history(params=params)
        except MichoWAPIError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result)


class WebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = WebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data['event']
        data = serializer.validated_data['data']

        if event == 'message.received':
            from_number = data.get('from', '')
            message_text = data.get('message', '')
            process_message(from_number, message_text)

        logger.info('WhatsApp webhook received: event=%s from=%s', event, data.get('from'))

        return Response({'status': 'ok'})
