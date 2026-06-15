from rest_framework import serializers
from .models import Province, Town, DeliveryMethod


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug']


class ProvinceAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug', 'sort_order']


class TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Town
        fields = ['id', 'province', 'name', 'slug']


class TownAdminSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = Town
        fields = ['id', 'province', 'province_name', 'name', 'slug']


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'name', 'description', 'price', 'estimated_days']


class DeliveryMethodAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'name', 'description', 'price', 'estimated_days', 'is_active', 'sort_order']
