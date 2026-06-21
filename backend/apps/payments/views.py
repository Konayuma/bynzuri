import hashlib
import hmac
import json
import logging
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import Payment
from apps.orders.models import Order
from .serializers import PaymentSerializer, PaymentInitiateSerializer, PaymentWebhookSerializer
from .lenco import lenco_service

logger = logging.getLogger(__name__)

OPERATOR_MAP = {
    'mtn_momo': 'mtn',
    'airtel_money': 'airtel',
    'zamtel_money': 'zamtel',
}


class PaymentInitiateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(
            Order, id=serializer.validated_data['order_id'],
            user=request.user
        )

        if order.status != 'awaiting_payment':
            return Response(
                {'detail': 'Order is not awaiting payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        method = serializer.validated_data['method']
        phone = serializer.validated_data['phone']
        operator = OPERATOR_MAP[method]

        idempotency_key = hashlib.sha256(
            f"{order.id}:{method}:{phone}".encode()
        ).hexdigest()

        if Payment.objects.filter(idempotency_key=idempotency_key).exists():
            existing = Payment.objects.get(idempotency_key=idempotency_key)
            return Response(
                PaymentSerializer(existing).data,
                status=status.HTTP_200_OK
            )

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            method=method,
            operator=operator,
            amount=order.grand_total,
            phone=phone,
            idempotency_key=idempotency_key,
        )

        lenco_result = lenco_service.initiate_collection(
            amount=float(order.grand_total),
            reference=idempotency_key,
            phone=phone,
            operator=operator,
        )

        if not lenco_result.get('status'):
            payment.status = 'failed'
            payment.gateway_response = lenco_result
            payment.save()
            return Response(
                {'detail': 'Payment initiation failed', 'error': lenco_result.get('message')},
                status=status.HTTP_502_BAD_GATEWAY
            )

        data = lenco_result.get('data', {})
        payment.lenco_id = data.get('id', '')
        payment.lenco_reference = data.get('lencoReference', '')
        payment.transaction_reference = data.get('reference', '')
        payment.status = 'processing' if data.get('status') == 'pay-offline' else 'pending'
        payment.gateway_response = data
        payment.fee = data.get('fee')
        payment.account_name = data.get('mobileMoneyDetails', {}).get('accountName', '')
        payment.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentStatusView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        payment = get_object_or_404(Payment, order_id=order_id, user=request.user)

        if payment.status in ('pending', 'processing'):
            lenco_result = lenco_service.get_collection_status(payment.idempotency_key)
            if lenco_result.get('status'):
                data = lenco_result.get('data', {})
                lenco_status = data.get('status')

                if lenco_status == 'successful':
                    payment.status = 'success'
                    payment.gateway_response = data
                    payment.fee = data.get('fee')
                    payment.account_name = data.get('mobileMoneyDetails', {}).get('accountName', '')
                    payment.save()

                    order = payment.order
                    order.status = 'paid'
                    order.save()
                elif lenco_status == 'failed':
                    payment.status = 'failed'
                    payment.gateway_response = data
                    payment.save()

        return Response(PaymentSerializer(payment).data)


class PaymentWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        signature = request.headers.get('X-Lenco-Signature', '')
        if not lenco_service.verify_webhook_signature(request.content, signature):
            logger.warning('Invalid Lenco webhook signature')
            return Response(
                {'detail': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            event = json.loads(request.body)
        except json.JSONDecodeError:
            return Response(
                {'detail': 'Invalid JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_type = event.get('event', '')
        data = event.get('data', {})

        if event_type not in ('collection.successful', 'collection.failed'):
            return Response({'status': 'ignored'})

        reference = data.get('reference', '')
        if not reference:
            return Response(
                {'detail': 'Missing reference'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(idempotency_key=reference)
        except Payment.DoesNotExist:
            try:
                payment = Payment.objects.get(transaction_reference=reference)
            except Payment.DoesNotExist:
                logger.warning(f'Payment not found for reference: {reference}')
                return Response({'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)

        if payment.status in ('success', 'failed'):
            return Response({'status': 'already_processed'})

        with transaction.atomic():
            payment.gateway_response = data
            payment.lenco_id = data.get('id', '')
            payment.lenco_reference = data.get('lencoReference', '')
            payment.fee = data.get('fee')
            payment.account_name = data.get('mobileMoneyDetails', {}).get('accountName', '')

            if event_type == 'collection.successful':
                payment.status = 'success'
                payment.transaction_reference = data.get('reference', payment.transaction_reference)
                payment.save()

                order = payment.order
                order.status = 'paid'
                order.save()
            else:
                payment.status = 'failed'
                payment.save()

        return Response({'status': 'ok'})
