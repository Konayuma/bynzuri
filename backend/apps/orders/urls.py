from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListCreateView.as_view(), name='order-list'),
    path('admin/', views.AdminOrderListView.as_view(), name='order-admin-list'),
    path('admin/<uuid:pk>/status/', views.AdminOrderStatusUpdateView.as_view(), name='order-admin-status'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]
