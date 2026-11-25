import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='effective_price', lookup_expr='gte', min_value=0)
    max_price = django_filters.NumberFilter(field_name='effective_price', lookup_expr='lte', min_value=0)
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category__slug']

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset
