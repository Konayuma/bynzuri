"""Public sitemap for the storefront, generated from the current catalog."""
from urllib.parse import quote
from xml.etree import ElementTree as ET

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_safe
from apps.products.models import Product


@require_safe
def sitemap(request):
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', namespace)
    root = ET.Element(f'{{{namespace}}}urlset')
    base = settings.PUBLIC_SITE_URL.rstrip('/')
    paths = ['/', '/catalog', '/help']
    paths.extend(f'/product/{quote(slug, safe="-")}' for slug in
                 Product.objects.filter(is_active=True).order_by('slug').values_list('slug', flat=True).iterator())
    for path in paths:
        entry = ET.SubElement(root, f'{{{namespace}}}url')
        ET.SubElement(entry, f'{{{namespace}}}loc').text = f'{base}{path}'
    response = HttpResponse(ET.tostring(root, encoding='utf-8', xml_declaration=True), content_type='application/xml; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=300'
    return response
