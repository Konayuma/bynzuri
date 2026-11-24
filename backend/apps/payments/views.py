import json
import logging
import uuid
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, views
from rest_framework.response import Response

from apps.orders.models import Order
from .lenco import lenco_service
from .models import Payment
from .serializers import PaymentInitiateSerializer, PaymentSerializer

logger = logging.getLogger(__name__)
OPERATOR_MAP = {'mtn_momo': 'mtn', 'airtel_money': 'airtel'}


def apply_provider_result(payment_id, data, expected_status=None):
    """Apply only a matching provider transaction, without regressing terminal states."""
    with transaction.atomic():
        payment = Payment.objects.select_for_update().select_related('order').get(pk=payment_id)
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        provider_status = data.get('status')
        if expected_status and provider_status != expected_status:
            return False
        try:
            matches = (data.get('reference') == payment.idempotency_key
                       and data.get('currency') == payment.currency
                       and Decimal(str(data.get('amount'))) == payment.amount)
        except (InvalidOperation, TypeError, ValueError):
            matches = False
        if not matches:
            logger.warning('Lenco transaction does not match payment %s', payment.id)
            return False
        if payment.status in ('success', 'failed', 'refunded'):
            return True
        payment.gateway_response = data
        payment.lenco_id = data.get('id') or payment.lenco_id
        payment.lenco_reference = data.get('lencoReference') or payment.lenco_reference
        payment.transaction_reference = data.get('reference') or payment.transaction_reference
        payment.fee = data.get('fee')
        mobile_details = data.get('mobileMoneyDetails')
        payment.account_name = (mobile_details.get('accountName') or '') if isinstance(mobile_details, dict) else ''
        if provider_status == 'successful':
            payment.status = 'success'
            if order.status == 'awaiting_payment':
                order.status = 'paid'
                order.save(update_fields=['status', 'updated_at'])
        elif provider_status == 'failed':
            payment.status = 'failed'
        elif provider_status == 'pay-offline':
            payment.status = 'processing'
        payment.save()
        return True


class PaymentInitiateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not lenco_service.configured:
            return Response({'detail': 'Mobile money payments are not configured yet.'}, status=503)
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), id=serializer.validated_data['order_id'], user=request.user)
            if order.status != 'awaiting_payment':
                return Response({'detail': 'Order is not awaiting payment.'}, status=400)
            if order.grand_total <= 0:
                return Response({'detail': 'The order total must be greater than zero for mobile money. Please contact the store.'}, status=400)
            existing = order.payments.filter(status__in=['pending', 'processing', 'success']).order_by('-created_at').first()
            if existing:
                return Response(PaymentSerializer(existing).data)
            method = serializer.validated_data['method']
            if order.payment_method != method:
                order.payment_method = method
                order.save(update_fields=['payment_method', 'updated_at'])
            payment = Payment.objects.create(order=order, user=request.user, method=method,
                operator=OPERATOR_MAP[method], amount=order.grand_total,
                phone=serializer.validated_data['phone'], idempotency_key=uuid.uuid4().hex)

        result = lenco_service.initiate_collection(amount=payment.amount, reference=payment.idempotency_key,
                                                   phone=payment.phone, operator=payment.operator)
        data = result.get('data')
        if result.get('status') and isinstance(data, dict):
            apply_provider_result(payment.id, data)
        elif result.get('rejected'):
            with transaction.atomic():
                locked = Payment.objects.select_for_update().get(pk=payment.id)
                if locked.status == 'pending':
                    locked.status = 'failed'
                    locked.save(update_fields=['status', 'updated_at'])
        # Transport errors are uncertain: never create another charge until reconciled.
        payment.refresh_from_db()
        response = dict(PaymentSerializer(payment).data)
        if payment.status == 'failed' and result.get('access_denied'):
            response['failure_reason'] = 'provider_access_denied'
        return Response(response, status=status.HTTP_201_CREATED)


class PaymentStatusView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        payment = Payment.objects.filter(order_id=order_id, user=request.user).order_by('-created_at').first()
        if payment is None:
            return Response({'detail': 'No payment found for this order.'}, status=404)
        verification_unavailable = False
        if payment.status in ('pending', 'processing'):
            result = lenco_service.get_collection_status(payment.idempotency_key)
            if result.get('status') and isinstance(result.get('data'), dict):
                verification_unavailable = not apply_provider_result(payment.id, result['data'])
                payment.refresh_from_db()
            else:
                verification_unavailable = True
        response = dict(PaymentSerializer(payment).data)
        if verification_unavailable:
            response['verification_unavailable'] = True
        return Response(response)


class PaymentWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        if not lenco_service.verify_webhook_signature(request.body, request.headers.get('X-Lenco-Signature', '')):
            return Response({'detail': 'Invalid signature.'}, status=401)
        try:
            event = json.loads(request.body)
            event_type = event.get('event')
            data = event.get('data')
            if not isinstance(data, dict):
                raise ValueError
        except (ValueError, AttributeError, UnicodeDecodeError):
            return Response({'detail': 'Invalid payload.'}, status=400)
        statuses = {'collection.successful': 'successful', 'collection.failed': 'failed'}
        if event_type not in statuses:
            return Response({'status': 'ignored'})
        payment = Payment.objects.filter(idempotency_key=data.get('reference')).first()
        if not payment:
            return Response({'detail': 'Payment not found.'}, status=404)
        if not apply_provider_result(payment.id, data, statuses[event_type]):
            return Response({'detail': 'Payment details do not match.'}, status=400)
        return Response({'status': 'ok'})
