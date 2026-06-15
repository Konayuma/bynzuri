from rest_framework import viewsets, filters, decorators, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'rating', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return Product.objects.all().select_related('category').prefetch_related('images')
        return super().get_queryset()

    @decorators.action(detail=False)
    def best_sellers(self, request):
        products = self.get_queryset().filter(rating__gte=4)[:8]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @decorators.action(detail=False)
    def new_arrivals(self, request):
        products = self.get_queryset()[:8]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
