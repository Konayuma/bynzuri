from django.urls import path
from . import views

urlpatterns = [
    path('provinces/', views.ProvinceViewSet.as_view({'get': 'list'}), name='province-list'),
    path('towns/', views.TownViewSet.as_view({'get': 'list'}), name='town-list'),
    path('methods/', views.DeliveryMethodViewSet.as_view({'get': 'list'}), name='delivery-method-list'),
]
