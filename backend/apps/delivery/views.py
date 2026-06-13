from rest_framework import viewsets
from .models import Province, Town, DeliveryMethod
from .serializers import ProvinceSerializer, TownSerializer, DeliveryMethodSerializer


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
