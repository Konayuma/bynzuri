from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'amount', 'status', 'transaction_reference', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=['mtn_momo', 'airtel_money', 'visa', 'mastercard'])


class PaymentWebhookSerializer(serializers.Serializer):
    transaction_reference = serializers.CharField()
    status = serializers.ChoiceField(choices=['success', 'failed'])
    idempotency_key = serializers.CharField()
    gateway_data = serializers.JSONField(required=False, default=dict)
