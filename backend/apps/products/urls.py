from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('best-sellers/', views.ProductViewSet.as_view({'get': 'best_sellers'}), name='product-best-sellers'),
    path('new-arrivals/', views.ProductViewSet.as_view({'get': 'new_arrivals'}), name='product-new-arrivals'),
    path('<slug:slug>/', views.ProductViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='product-detail'),
]
