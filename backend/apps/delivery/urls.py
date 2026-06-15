from django.urls import path
from . import views

urlpatterns = [
    path('provinces/', views.ProvinceViewSet.as_view({'get': 'list'}), name='province-list'),
    path('towns/', views.TownViewSet.as_view({'get': 'list'}), name='town-list'),
    path('methods/', views.DeliveryMethodViewSet.as_view({'get': 'list'}), name='delivery-method-list'),
    path('admin/provinces/', views.ProvinceAdminViewSet.as_view({
        'get': 'list', 'post': 'create',
    }), name='admin-province-list'),
    path('admin/provinces/<uuid:pk>/', views.ProvinceAdminViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='admin-province-detail'),
    path('admin/towns/', views.TownAdminViewSet.as_view({
        'get': 'list', 'post': 'create',
    }), name='admin-town-list'),
    path('admin/towns/<uuid:pk>/', views.TownAdminViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='admin-town-detail'),
    path('admin/methods/', views.DeliveryMethodAdminViewSet.as_view({
        'get': 'list', 'post': 'create',
    }), name='admin-delivery-method-list'),
    path('admin/methods/<uuid:pk>/', views.DeliveryMethodAdminViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='admin-delivery-method-detail'),
]
