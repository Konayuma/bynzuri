from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Province, Town, DeliveryMethod
from .serializers import (
    ProvinceSerializer, ProvinceAdminSerializer,
    TownSerializer, TownAdminSerializer,
    DeliveryMethodSerializer, DeliveryMethodAdminSerializer,
)


class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = None


class TownViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Town.objects.all()
    serializer_class = TownSerializer
    pagination_class = None
    filterset_fields = ['province']


class DeliveryMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DeliveryMethod.objects.filter(is_active=True)
    serializer_class = DeliveryMethodSerializer
    pagination_class = None


class ProvinceAdminViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


class TownAdminViewSet(viewsets.ModelViewSet):
    queryset = Town.objects.all()
    serializer_class = TownAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    filterset_fields = ['province']


class DeliveryMethodAdminViewSet(viewsets.ModelViewSet):
    queryset = DeliveryMethod.objects.all()
    serializer_class = DeliveryMethodAdminSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
