from django.contrib import admin
from .models import WhatsAppMessage


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['to_number', 'direction', 'status', 'message_type', 'created_at']
    list_filter = ['direction', 'status', 'message_type']
    search_fields = ['to_number', 'body', 'wapi_message_id']
