from rest_framework import serializers
from django.utils.text import slugify
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    slug = serializers.SlugField(required=False, allow_blank=True, max_length=120)

    def validate(self, attrs):
        if not self.instance and not attrs.get('slug'):
            slug = slugify(attrs.get('name', ''))
            if not slug:
                raise serializers.ValidationError({'name': 'Use a name containing letters or numbers for the category URL.'})
            attrs['slug'] = slug[:120]
        slug = attrs.get('slug')
        if slug and Category.objects.filter(slug=slug).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError({'name': 'A category with this name or URL already exists.'})
        return attrs

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'description', 'product_count', 'sort_order']
