from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import views, permissions
from rest_framework.response import Response
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import User


class DashboardView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        try:
            days = int(request.query_params.get('days', 30))
        except (TypeError, ValueError):
            days = 0
        if days not in (7, 30, 90):
            return Response({'detail': 'Choose a period of 7, 30, or 90 days.'}, status=400)

        paid_orders = Order.objects.filter(status__in=['paid', 'processing', 'dispatched', 'delivered'])
        total_revenue = paid_orders.aggregate(total=Sum('grand_total'))['total'] or 0
        today = timezone.localdate()
        start = today - timedelta(days=days - 1)
        period_orders = paid_orders.filter(created_at__date__gte=start, created_at__date__lte=today)
        daily = period_orders.annotate(day=TruncDate('created_at')).values('day').annotate(
            revenue=Sum('grand_total'), orders=Count('id')
        )
        by_day = {row['day']: row for row in daily}
        sales_history = [
            {'date': day.isoformat(), 'revenue': by_day.get(day, {}).get('revenue', Decimal('0.00')),
             'orders': by_day.get(day, {}).get('orders', 0)}
            for day in (start + timedelta(days=i) for i in range(days))
        ]
        period_totals = period_orders.aggregate(revenue=Sum('grand_total'), orders=Count('id'))
        line_total = ExpressionWrapper(F('quantity') * F('price_at_purchase'), output_field=DecimalField(max_digits=20, decimal_places=2))
        top_products = list(OrderItem.objects.filter(order__in=period_orders).values('product_title').annotate(
            units=Sum('quantity'), revenue=Sum(line_total)
        ).order_by('-revenue', 'product_title')[:5])

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
            'period_days': days,
            'period_revenue': period_totals['revenue'] or Decimal('0.00'),
            'period_orders': period_totals['orders'],
            'sales_history': sales_history,
            'top_products': top_products,
        })
