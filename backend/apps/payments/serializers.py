from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'method', 'operator', 'amount', 'currency',
            'status', 'transaction_reference', 'lenco_reference', 'phone',
            'fee', 'account_name', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'lenco_reference', 'fee', 'account_name']


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    method = serializers.ChoiceField(choices=['mtn_momo', 'airtel_money', 'zamtel_money'])
    phone = serializers.CharField(max_length=20)

    def validate_method(self, value):
        method_operator_map = {
            'mtn_momo': 'mtn',
            'airtel_money': 'airtel',
            'zamtel_money': 'zamtel',
        }
        return value

    def validate_phone(self, value):
        cleaned = value.replace(' ', '').replace('-', '')
        if not cleaned.startswith('260'):
            cleaned = f'260{cleaned.lstrip("0")}'
        return cleaned


class PaymentWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    data = serializers.DictField()
