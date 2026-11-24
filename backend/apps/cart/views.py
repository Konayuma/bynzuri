from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
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

    @transaction.atomic
    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_or_create_cart(request.user)
        cart = Cart.objects.select_for_update().get(pk=cart.pk)
        product = get_object_or_404(Product.objects.select_for_update(), id=serializer.validated_data['product'])
        existing = CartItem.objects.filter(cart=cart, product=product).first()
        desired = serializer.validated_data['quantity'] + (existing.quantity if existing else 0)
        if not product.is_active or desired > product.stock:
            return Response({'detail': 'This product is unavailable in the requested quantity.'}, status=400)

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

    @transaction.atomic
    def patch(self, request, item_id):
        cart = get_or_create_cart(request.user)
        cart = Cart.objects.select_for_update().get(pk=cart.pk)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        serializer = CartItemUpdateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = Product.objects.select_for_update().get(pk=item.product_id)
        if not product.is_active or serializer.validated_data.get('quantity', item.quantity) > product.stock:
            return Response({'detail': 'This product is unavailable in the requested quantity.'}, status=400)
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

    @transaction.atomic
    def post(self, request):
        serializer = CartMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_or_create_cart(request.user)
        cart = Cart.objects.select_for_update().get(pk=cart.pk)
        skipped = []

        indexed_items = list(enumerate(serializer.validated_data['items']))
        for index, raw_item in sorted(indexed_items, key=lambda entry: str(entry[1].get('product', ''))):
            item_serializer = CartItemCreateSerializer(data=raw_item)
            if not item_serializer.is_valid():
                skipped.append({'index': index, 'reason': 'Invalid product or quantity.'})
                continue
            item_data = item_serializer.validated_data
            product = Product.objects.select_for_update().filter(id=item_data['product']).first()
            if not product:
                skipped.append({'index': index, 'reason': 'Product no longer exists.'})
                continue
            existing = CartItem.objects.filter(cart=cart, product=product).first()
            desired = max(item_data['quantity'], existing.quantity if existing else 0)
            if not product.is_active or desired > product.stock:
                skipped.append({'index': index, 'reason': 'Product is unavailable in the requested quantity.'})
                continue
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': item_data['quantity']}
            )
            if not created and item_data['quantity'] > item.quantity:
                item.quantity = item_data['quantity']
                item.save()

        cart_serializer = CartSerializer(cart)
        return Response({**cart_serializer.data, 'skipped': skipped})
