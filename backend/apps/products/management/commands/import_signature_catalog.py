"""Import the products and prices already displayed in the signature collection."""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categories.models import Category
from apps.products.models import Product

# Stock is unknown: new entries default to zero until an administrator confirms it.
PRODUCTS = (
    ('Growth Elixir', 'growth-elixir', 'hair-growth', '185.00'),
    ('Nourishing Oil Mix', 'nourishing-oil-mix', 'oils', '90.00'),
    ('Mini Whipped Shea Butter (60 g)', 'mini-whipped-shea-butter-60g', 'beauty-essentials', '100.00'),
    ('Shampoo Bar', 'shampoo-bar', 'hair-care', '60.00'),
    ('Deep Conditioner', 'deep-conditioner', 'hair-care', '200.00'),
    ('Leave-in Conditioner', 'leave-in-conditioner', 'hair-care', '200.00'),
    ('Herbal Hair Mist', 'herbal-hair-mist', 'hair-care', '150.00'),
    ('Exfoliating Toner', 'exfoliating-toner', 'beauty-essentials', '150.00'),
)
CATEGORIES = {
    'hair-care': ('Hair Care', 1),
    'hair-growth': ('Hair Growth', 2),
    'oils': ('Oils', 3),
    'beauty-essentials': ('Beauty Essentials', 6),
}


class Command(BaseCommand):
    help = 'Import missing signature-collection products without changing existing records.'

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for slug, (name, order) in CATEGORIES.items():
            categories[slug], _ = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'sort_order': order}
            )
        for title, slug, category, price in PRODUCTS:
            _, created = Product.objects.get_or_create(
                slug=slug,
                defaults={'title': title, 'category': categories[category],
                          'description': '', 'price': Decimal(price), 'stock': 0},
            )
            self.stdout.write(f"{'Created' if created else 'Kept existing'}: {title}")
        self.stdout.write('New products have zero stock until an administrator updates availability.')
