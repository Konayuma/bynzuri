import hashlib
import hmac
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import Payment
from apps.orders.models import Order
from .serializers import PaymentSerializer, PaymentInitiateSerializer, PaymentWebhookSerializer


class PaymentInitiateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data['order_id'], user=request.user)

        if order.status != 'awaiting_payment':
            return Response(
                {'detail': 'Order is not awaiting payment'},
                status=status.HTTP_400_BAD_REQUEST
            )

        idempotency_key = hashlib.sha256(
            f"{order.id}:{serializer.validated_data['method']}".encode()
        ).hexdigest()

        if Payment.objects.filter(idempotency_key=idempotency_key).exists():
            return Response(
                {'detail': 'Payment already initiated'},
                status=status.HTTP_409_CONFLICT
            )

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            method=serializer.validated_data['method'],
            amount=order.grand_total,
            idempotency_key=idempotency_key,
        )

        payment_data = PaymentSerializer(payment).data
        payment_data['payment_url'] = f"https://payments.bynzuri.com/pay/{payment.id}"

        return Response(payment_data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = get_object_or_404(
            Payment,
            idempotency_key=serializer.validated_data['idempotency_key']
        )

        if payment.status != 'pending':
            return Response({'status': 'already_processed'})

        with transaction.atomic():
            payment.status = serializer.validated_data['status']
            payment.transaction_reference = serializer.validated_data['transaction_reference']
            payment.gateway_response = serializer.validated_data.get('gateway_data')
            payment.save()

            if serializer.validated_data['status'] == 'success':
                order = payment.order
                order.status = 'paid'
                order.save()

        return Response({'status': 'ok'})


class PaymentStatusView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        payment = get_object_or_404(Payment, order_id=order_id, user=request.user)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
