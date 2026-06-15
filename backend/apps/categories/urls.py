from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryViewSet.as_view({
        'get': 'list', 'post': 'create',
    }), name='category-list'),
    path('<slug:slug>/', views.CategoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='category-detail'),
]
