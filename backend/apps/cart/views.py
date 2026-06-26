from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from apps.products.models import Product
from .serializers import (
    CartSerializer, CartItemSerializer,
    CartItemCreateSerializer, CartItemUpdateSerializer,
    CartMergeSerializer
)


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        # Prefetch products to prevent N+1 in CartSerializer computed fields.
        cart_items_qs = cart.items.select_related('product').all()
        cart._prefetched_objects_cache = getattr(cart, '_prefetched_objects_cache', {})
        cart._prefetched_objects_cache['items'] = cart_items_qs
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddItemView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=serializer.validated_data['product'])
        cart = get_or_create_cart(request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': serializer.validated_data['quantity']}
        )

        if not created:
            item.quantity += serializer.validated_data['quantity']
            item.save()

        # Ensure subtotal/total calculation won't N+1 (Cart items -> product)
        cart_items_qs = cart.items.select_related('product').all()
        cart._prefetched_objects_cache = getattr(cart, '_prefetched_objects_cache', {})
        cart._prefetched_objects_cache['items'] = cart_items_qs

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        serializer = CartItemUpdateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)

    def delete(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


class CartMergeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_or_create_cart(request.user)

        for item_data in serializer.validated_data['items']:
            product = get_object_or_404(Product, id=item_data['product'])
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': item_data['quantity']}
            )
            if not created and item_data['quantity'] > item.quantity:
                item.quantity = item_data['quantity']
                item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
