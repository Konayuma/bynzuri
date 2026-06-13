"""
Seed script to populate provinces, towns, delivery methods, and sample categories.
Run: python manage.py shell < scripts/seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.delivery.models import Province, Town, DeliveryMethod
from apps.categories.models import Category

# Provinces of Zambia
provinces_data = [
    ("Central", "central"),
    ("Copperbelt", "copperbelt"),
    ("Eastern", "eastern"),
    ("Luapula", "luapula"),
    ("Lusaka", "lusaka"),
    ("Muchinga", "muchinga"),
    ("Northern", "northern"),
    ("North-Western", "north-western"),
    ("Southern", "southern"),
    ("Western", "western"),
]

towns_data = {
    "central": ["Kabwe", "Mkushi", "Mumbwa", "Serenje", "Chibombo", "Kapiri Mposhi"],
    "copperbelt": ["Kitwe", "Ndola", "Chingola", "Mufulira", "Luanshya", "Kalulushi", "Chililabombwe"],
    "eastern": ["Chipata", "Petauke", "Katete", "Lundazi", "Nyimba", "Sinda"],
    "luapula": ["Mansa", "Nchelenge", "Samfya", "Mwansabombwe", "Kawambwa"],
    "lusaka": ["Lusaka", "Chongwe", "Kafue", "Rufunsa", "Luangwa"],
    "muchinga": ["Chinsali", "Isoka", "Nakonde", "Mpika", "Shiwang'andu"],
    "northern": ["Kasama", "Mpulungu", "Mbala", "Luwingu", "Mungwi"],
    "north-western": ["Solwezi", "Mwinilunga", "Kasempa", "Zambezi", "Kabompo"],
    "southern": ["Livingstone", "Choma", "Monze", "Mazabuka", "Kalomo", "Siavonga"],
    "western": ["Mongu", "Senanga", "Sesheke", "Kaoma", "Limulunga", "Lukulu"],
}

delivery_methods_data = [
    {"name": "Lusaka Delivery", "description": "Same-day and next-day delivery within Lusaka", "price": 35, "days": "1-2 days", "sort": 1},
    {"name": "Intercity Courier", "description": "Courier delivery to major towns across Zambia", "price": 65, "days": "2-5 days", "sort": 2},
    {"name": "Bus Freight", "description": "Economy bus freight to all provinces", "price": 45, "days": "3-7 days", "sort": 3},
    {"name": "Store Pickup", "description": "Pick up from our Lusaka showroom", "price": 0, "days": "Same day", "sort": 4},
]

categories_data = [
    {"name": "Hair Care", "slug": "hair-care", "sort": 1},
    {"name": "Hair Growth", "slug": "hair-growth", "sort": 2},
    {"name": "Oils", "slug": "oils", "sort": 3},
    {"name": "Wigs", "slug": "wigs", "sort": 4},
    {"name": "Accessories", "slug": "accessories", "sort": 5},
    {"name": "Beauty Essentials", "slug": "beauty-essentials", "sort": 6},
]

# Seed provinces and towns
for name, slug in provinces_data:
    province, created = Province.objects.get_or_create(
        slug=slug,
        defaults={"name": name, "sort_order": provinces_data.index((name, slug))}
    )
    if created:
        print(f"Created province: {name}")
        for town_name in towns_data.get(slug, []):
            Town.objects.create(province=province, name=town_name, slug=town_name.lower().replace(" ", "-"))
            print(f"  Created town: {town_name}")
    else:
        print(f"Province already exists: {name}")

# Seed delivery methods
for dm in delivery_methods_data:
    _, created = DeliveryMethod.objects.get_or_create(
        name=dm["name"],
        defaults={
            "description": dm["description"],
            "price": dm["price"],
            "estimated_days": dm["days"],
            "sort_order": dm["sort"],
        }
    )
    if created:
        print(f"Created delivery method: {dm['name']}")

# Seed categories
for cat in categories_data:
    _, created = Category.objects.get_or_create(
        slug=cat["slug"],
        defaults={"name": cat["name"], "sort_order": cat["sort"]}
    )
    if created:
        print(f"Created category: {cat['name']}")

print("\nSeed completed!")
