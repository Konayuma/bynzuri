from rest_framework import viewsets, filters, decorators, permissions, views, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import DecimalField, ExpressionWrapper, F, Value, Subquery
from django.db.models.functions import Round, Coalesce, Greatest
from .models import Product, ProductImage, StoreDiscount
from .filters import ProductFilter
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer,
    ProductImageSerializer, ProductImageCreateSerializer,
)


class SalePriceOrderingFilter(filters.OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        return [('effective_price' if field == 'price' else '-effective_price' if field == '-price' else field) for field in ordering] if ordering else ordering


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, SalePriceOrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['title', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'rating', 'title']
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action in ('retrieve', 'admin_list'):
            return ProductDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProductCreateSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'admin_list'):
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'admin_list'):
            queryset = Product.objects.all().select_related('category').prefetch_related('images')
        else:
            queryset = super().get_queryset()
        decimal = DecimalField(max_digits=5, decimal_places=2)
        queryset = queryset.annotate(store_discount=Coalesce(Subquery(StoreDiscount.objects.filter(pk=1).values('percent')[:1]), Value(0, output_field=decimal)))
        amount = ExpressionWrapper(F('price') * (Value(100) - Greatest(F('discount_percent'), F('store_discount'))) / Value(100), output_field=DecimalField(max_digits=12, decimal_places=4))
        return queryset.annotate(effective_price=Round(amount, 2))

    def admin_list(self, request):
        return self.list(request)

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


class StoreDiscountView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        discount = StoreDiscount.objects.filter(pk=1).first()
        return Response({'percent': str(discount.percent) if discount else '0.00'})

    def put(self, request):
        from rest_framework import serializers
        field = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
        try:
            percent = field.run_validation(request.data.get('percent'))
        except serializers.ValidationError as exc:
            return Response({'percent': exc.detail}, status=400)
        StoreDiscount.objects.update_or_create(pk=1, defaults={'percent': percent})
        return Response({'percent': str(percent)})

class ProductImageUploadView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductImageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(product=product)
        return Response(
            ProductImageSerializer(image).data,
            status=status.HTTP_201_CREATED
        )


class ProductImageDeleteView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, slug, image_id):
        product = get_object_or_404(Product, slug=slug)
        image = get_object_or_404(ProductImage, id=image_id, product=product)
        image.image.delete(save=False)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignatureCatalogImportView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        from .management.commands.import_signature_catalog import import_catalog
        created, skipped = import_catalog()
        return Response({'created': created, 'skipped': skipped})
