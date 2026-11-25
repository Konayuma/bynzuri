import hashlib
import uuid
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.products.models import Product
from .serializers import OrderListSerializer, OrderCreateSerializer, AdminOrderSerializer, OrderStatusUpdateSerializer
from .services import OrderTransitionError, transition_order


class OrderListCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Older clients may omit the key; cart locking still prevents concurrent consumption.
        raw_key = str(serializer.validated_data.get('checkout_key') or uuid.uuid4())
        idempotency_key = hashlib.sha256(f'{request.user.id}:{raw_key}'.encode()).hexdigest()

        with transaction.atomic():
            # A cart row persists across orders and serializes concurrent checkouts for this user.
            cart = Cart.objects.select_for_update().filter(user=request.user).first()
            existing = Order.objects.filter(user=request.user, idempotency_key=idempotency_key).first()
            if existing:
                return Response(OrderListSerializer(existing).data, status=status.HTTP_200_OK)
            if not cart:
                return Response({'detail': 'Cart is empty'}, status=400)
            cart_items = list(cart.items.select_related('product').all())
            if not cart_items:
                return Response({'detail': 'Cart is empty'}, status=400)

            from apps.delivery.models import DeliveryMethod
            try:
                delivery = DeliveryMethod.objects.filter(id=serializer.validated_data['delivery_method'], is_active=True).first()
            except (ValueError, TypeError, ValidationError):
                delivery = None
            if not delivery:
                return Response({'detail': 'This delivery method is unavailable. Please select another.'}, status=400)

            # Validate every line before changing any stock.
            products = {p.id: p for p in Product.objects.select_for_update().filter(
                id__in=[item.product_id for item in cart_items]).order_by('id')}
            for item in cart_items:
                product = products[item.product_id]
                if not product.is_active or product.stock < item.quantity:
                    return Response({'detail': f'Insufficient stock for {product.title}'}, status=400)

            total_amount = 0
            order_items_data = []
            for item in cart_items:
                product = products[item.product_id]
                product.stock -= item.quantity
                product.save(update_fields=['stock'])
                total_amount += product.sale_price * item.quantity
                order_items_data.append({'product': product, 'product_title': product.title,
                                         'quantity': item.quantity, 'price_at_purchase': product.sale_price})

            order = Order.objects.create(
                user=request.user, idempotency_key=idempotency_key, total_amount=total_amount,
                delivery_fee=delivery.price, grand_total=total_amount + delivery.price,
                province=serializer.validated_data['province'], town=serializer.validated_data['town'],
                street_address=serializer.validated_data['street_address'], phone=serializer.validated_data['phone'],
                delivery_method=serializer.validated_data['delivery_method'], payment_method=serializer.validated_data['payment_method'],
                notes=serializer.validated_data.get('notes', '')
            )
            OrderItem.objects.bulk_create([OrderItem(order=order, **item) for item in order_items_data])
            cart.items.all().delete()

        result_serializer = OrderListSerializer(order)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderListSerializer(order)
        return Response(serializer.data)


class AdminOrderListView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)

        paginator = PageNumberPagination()
        paginator.page_size = 20
        page_orders = paginator.paginate_queryset(orders, request, view=self)
        serializer = AdminOrderSerializer(page_orders, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminOrderStatusUpdateView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        get_object_or_404(Order, id=pk)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = transition_order(pk, serializer.validated_data['status'])
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        except OrderTransitionError as error:
            return Response({'detail': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AdminOrderSerializer(order).data)
