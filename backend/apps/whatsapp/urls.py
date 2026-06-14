from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.SendMessageView.as_view(), name='whatsapp-send'),
    path('history/', views.MessageHistoryView.as_view(), name='whatsapp-history'),
    path('webhook/', views.WebhookView.as_view(), name='whatsapp-webhook'),
]
