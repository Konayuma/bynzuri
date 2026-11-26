from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import path, include
from apps.users.views import SupportInquiryCreateView
from .sitemap import sitemap


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return JsonResponse({'status': 'healthy', 'database': 'connected'})
    except Exception:
        return JsonResponse({'status': 'unhealthy', 'database': 'unavailable'}, status=503)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/sitemap/', sitemap, name='storefront-sitemap'),
    path('api/auth/', include('apps.users.urls')),
    path('api/support/inquiries/', SupportInquiryCreateView.as_view(), name='support-inquiry-create'),
    path('api/products/', include('apps.products.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/whatsapp/', include('apps.whatsapp.urls')),
]
