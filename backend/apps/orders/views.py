import hashlib
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.products.models import Product
from .serializers import OrderListSerializer, OrderCreateSerializer


class OrderListCreateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.select_related('product').all()

        if not cart_items:
            return Response(
                {'detail': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        idempotency_input = f"{request.user.id}:{cart.id}"
        idempotency_key = hashlib.sha256(idempotency_input.encode()).hexdigest()

        if Order.objects.filter(idempotency_key=idempotency_key).exists():
            return Response(
                {'detail': 'Order already submitted'},
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():
            total_amount = 0
            order_items_data = []

            for cart_item in cart_items:
                product = Product.objects.select_for_update().get(id=cart_item.product.id)

                if product.stock < cart_item.quantity:
                    return Response(
                        {'detail': f'Insufficient stock for {product.title}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                product.stock -= cart_item.quantity
                product.save()

                line_total = product.price * cart_item.quantity
                total_amount += line_total

                order_items_data.append({
                    'product': product,
                    'product_title': product.title,
                    'quantity': cart_item.quantity,
                    'price_at_purchase': product.price
                })

            from apps.delivery.models import DeliveryMethod
            delivery = DeliveryMethod.objects.filter(
                id=serializer.validated_data['delivery_method']
            ).first()
            delivery_fee = delivery.price if delivery else 0

            order = Order.objects.create(
                user=request.user,
                idempotency_key=idempotency_key,
                total_amount=total_amount,
                delivery_fee=delivery_fee,
                grand_total=total_amount + delivery_fee,
                province=serializer.validated_data['province'],
                town=serializer.validated_data['town'],
                street_address=serializer.validated_data['street_address'],
                phone=serializer.validated_data['phone'],
                delivery_method=serializer.validated_data['delivery_method'],
                payment_method=serializer.validated_data['payment_method'],
                notes=serializer.validated_data.get('notes', '')
            )

            for item_data in order_items_data:
                OrderItem.objects.create(order=order, **item_data)

            cart_items.delete()

        result_serializer = OrderListSerializer(order)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, user=request.user)
        serializer = OrderListSerializer(order)
        return Response(serializer.data)
