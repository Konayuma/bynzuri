from rest_framework import serializers
from django.utils.text import slugify
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'category_slug', 'title', 'slug',
            'price', 'stock', 'is_in_stock', 'images',
            'rating', 'review_count', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'category_slug', 'title', 'slug',
            'description', 'price', 'stock', 'is_in_stock', 'is_active', 'is_featured', 'images',
            'rating', 'review_count', 'created_at', 'updated_at'
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=250)
    description = serializers.CharField(required=False, allow_blank=True)
    images = ProductImageSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            'category', 'title', 'slug', 'description', 'price', 'stock',
            'is_active', 'is_featured', 'images',
        ]

    def validate(self, attrs):
        if not self.instance and not attrs.get('slug'):
            slug = slugify(attrs.get('title', ''))[:250]
            if not slug:
                raise serializers.ValidationError({'title': 'Use a title containing letters or numbers for the product URL.'})
            attrs['slug'] = slug
        if attrs.get('slug'):
            attrs['slug'] = self.validate_slug(attrs['slug'])
        return attrs

    def validate_slug(self, value):
        if not value:
            return value
        qs = Product.objects.filter(slug=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError('A product with this slug already exists.')
        return value


class ProductImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']
        read_only_fields = ['id']
