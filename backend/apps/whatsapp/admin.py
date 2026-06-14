from django.contrib import admin
from .models import WhatsAppMessage, Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'state', 'updated_at', 'created_at']
    list_filter = ['state']
    search_fields = ['phone_number']


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['to_number', 'direction', 'status', 'message_type', 'created_at']
    list_filter = ['direction', 'status', 'message_type']
    search_fields = ['to_number', 'body', 'wapi_message_id']
