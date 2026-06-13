from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.PaymentInitiateView.as_view(), name='payment-initiate'),
    path('webhook/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    path('status/<uuid:order_id>/', views.PaymentStatusView.as_view(), name='payment-status'),
]
