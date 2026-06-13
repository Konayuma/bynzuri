from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart-detail'),
    path('add/', views.CartAddItemView.as_view(), name='cart-add'),
    path('merge/', views.CartMergeView.as_view(), name='cart-merge'),
    path('items/<uuid:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
]
