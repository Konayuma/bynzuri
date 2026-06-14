from rest_framework import serializers
from .models import WhatsAppMessage


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'order', 'user', 'direction', 'status',
            'to_number', 'from_number', 'body', 'message_type',
            'wapi_message_id', 'error_message', 'created_at',
        ]
        read_only_fields = [
            'id', 'status', 'wapi_message_id', 'error_message',
            'created_at', 'updated_at',
        ]


class SendTextSerializer(serializers.Serializer):
    to = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=4096)


class WebhookSerializer(serializers.Serializer):
    event = serializers.CharField()
    session_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    data = serializers.JSONField()
