from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from rest_framework import views, permissions
from rest_framework.response import Response
from apps.orders.models import Order
from apps.products.models import Product
from apps.users.models import User


class DashboardView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_revenue = Order.objects.filter(
            status__in=['paid', 'processing', 'dispatched', 'delivered']
        ).aggregate(total=Sum('grand_total'))['total'] or 0

        total_orders = Order.objects.count()
        total_products = Product.objects.filter(is_active=True).count()
        total_customers = User.objects.filter(role='customer', is_active=True).count()

        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        )

        recent_orders = Order.objects.order_by('-created_at')[:5].values(
            'id', 'status', 'grand_total', 'created_at'
        )

        low_stock = Product.objects.filter(is_active=True, stock__lte=5).values(
            'id', 'title', 'stock'
        )[:10]

        return Response({
            'revenue': total_revenue,
            'orders': total_orders,
            'products': total_products,
            'customers': total_customers,
            'orders_by_status': orders_by_status,
            'recent_orders': recent_orders,
            'low_stock': low_stock,
        })
