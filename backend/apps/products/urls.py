from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('import-signature/', views.SignatureCatalogImportView.as_view(), name='product-import-signature'),
    path('manage/', views.ProductViewSet.as_view({'get': 'admin_list'}), name='product-manage'),
    path('best-sellers/', views.ProductViewSet.as_view({'get': 'best_sellers'}), name='product-best-sellers'),
    path('new-arrivals/', views.ProductViewSet.as_view({'get': 'new_arrivals'}), name='product-new-arrivals'),
    path('<slug:slug>/', views.ProductViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='product-detail'),
    path('<slug:slug>/images/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('<slug:slug>/images/<uuid:image_id>/', views.ProductImageDeleteView.as_view(), name='product-image-delete'),
]
