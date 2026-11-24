from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Review
from apps.products.models import Product
from .serializers import ReviewSerializer


class ReviewOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.user_id == request.user.id or request.user.is_staff


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ReviewOwnerOrStaff]

    def get_queryset(self):
        queryset = Review.objects.all() if self.request.user.is_staff else Review.objects.filter(is_approved=True)
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = Review.objects.filter(Q(is_approved=True) | Q(user=self.request.user))
        product_slug = self.request.query_params.get('product')
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        product_slug = request.data.get('product_slug')
        if not product_slug:
            return Response(
                {'detail': 'product_slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        product = get_object_or_404(Product, slug=product_slug)
        if Review.objects.filter(product=product, user=request.user).exists():
            return Response({'detail': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user, product=product)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save(is_approved=False)

    @transaction.atomic
    def perform_destroy(self, instance):
        instance.delete()
