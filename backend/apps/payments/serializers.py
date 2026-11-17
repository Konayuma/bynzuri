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
    method = serializers.ChoiceField(choices=['mtn_momo', 'airtel_money'])
    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        import re
        cleaned = re.sub(r'[\s()-]', '', value)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if re.fullmatch(r'0[679]\d{8}', cleaned):
            cleaned = '260' + cleaned[1:]
        if not re.fullmatch(r'260[679]\d{8}', cleaned):
            raise serializers.ValidationError('Enter a valid Zambian mobile number.')
        return cleaned


class PaymentWebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    data = serializers.DictField()
