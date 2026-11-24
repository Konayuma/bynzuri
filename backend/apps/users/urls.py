from django.urls import path
from .session_views import CookieTokenView, CookieRefreshView, CsrfView, LogoutView
from . import views

urlpatterns = [
    path('csrf/', CsrfView.as_view(), name='csrf'),
    path('token/', CookieTokenView.as_view(), name='token-obtain'),
    path('token/refresh/', CookieRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<uuid:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', views.ResendVerificationEmailView.as_view(), name='resend-verification'),
]
