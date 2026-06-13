from rest_framework import serializers
from .models import Province, Town, DeliveryMethod


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name', 'slug']


class TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Town
        fields = ['id', 'province', 'name', 'slug']


class DeliveryMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryMethod
        fields = ['id', 'name', 'description', 'price', 'estimated_days']
