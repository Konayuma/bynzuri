from django.contrib import admin
from .models import User, Address, EmailVerification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'town', 'province', 'is_default']
    list_filter = ['province']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'sent_requested_at', 'expires_at', 'send_attempts', 'last_error']
    list_filter = ['status']
    search_fields = ['user__email']
    fields = ['user', 'status', 'sent_requested_at', 'expires_at', 'attempts', 'send_attempts', 'last_error', 'provider_id']
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
