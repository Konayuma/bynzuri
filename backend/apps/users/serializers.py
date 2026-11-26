from rest_framework import serializers
import re
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from apps.delivery.models import Province, Town
from .models import User, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'is_staff', 'email_verified']
        read_only_fields = ['id', 'role', 'is_staff', 'email_verified']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone']

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            is_active=False,
        )
        return user


class AddressSerializer(serializers.ModelSerializer):
    province_name = serializers.SerializerMethodField()
    town_name = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ['id', 'province', 'province_name', 'town', 'town_name', 'street_address', 'phone', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']

    def _name(self, model, value):
        try:
            return model.objects.filter(pk=value).values_list('name', flat=True).first() or value
        except (ValueError, TypeError, DjangoValidationError):
            return value

    def get_province_name(self, obj):
        return self._name(Province, obj.province)

    def get_town_name(self, obj):
        return self._name(Town, obj.town)

    def validate_phone(self, value):
        if not re.fullmatch(r'(?:\+?260|0)[0-9]{9}', re.sub(r'[\s()-]', '', value)):
            raise serializers.ValidationError('Enter a valid Zambian phone number.')
        return value.strip()

    def validate(self, attrs):
        if self.instance and not {'province', 'town'} & attrs.keys():
            return attrs
        province = attrs.get('province', getattr(self.instance, 'province', ''))
        town = attrs.get('town', getattr(self.instance, 'town', ''))
        try:
            valid = Town.objects.filter(pk=town, province_id=province).exists()
        except (ValueError, TypeError, DjangoValidationError):
            valid = False
        if not valid:
            raise serializers.ValidationError({'town': 'Select a valid town in the chosen province.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data['user']
        User.objects.select_for_update().get(pk=user.pk)
        if validated_data.get('is_default'):
            Address.objects.filter(user=user, is_default=True).update(is_default=False)
        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        User.objects.select_for_update().get(pk=instance.user_id)
        if validated_data.get('is_default'):
            Address.objects.filter(user_id=instance.user_id, is_default=True).exclude(pk=instance.pk).update(is_default=False)
        return super().update(instance, validated_data)
