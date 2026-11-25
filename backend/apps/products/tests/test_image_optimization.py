import io
import logging
import tempfile
from unittest.mock import patch
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.categories.models import Category
from apps.products.models import Product, ProductImage


def make_test_png(name='sample.png'):
    buf = io.BytesIO()
    Image.new('RGB', (100, 100), color=(200, 100, 120)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class ProductImageOptimizationTests(TestCase):
    def setUp(self):
        self._media_dir = tempfile.TemporaryDirectory()
        self._override = override_settings(MEDIA_ROOT=self._media_dir.name)
        self._override.enable()
        self.addCleanup(self._override.disable)
        self.addCleanup(self._media_dir.cleanup)

        self.category = Category.objects.create(name='Oils', slug='oils')
        self.product = Product.objects.create(
            category=self.category,
            title='Glow Oil',
            slug='glow-oil',
            description='Nourishing oil',
            price='120.00',
            stock=5,
        )

    def test_metadata_update_does_not_reoptimize_committed_image(self):
        img = ProductImage.objects.create(
            product=self.product,
            image=make_test_png(),
            alt_text='Initial alt',
        )
        self.assertTrue(img.image.name.endswith('.webp'))

        with patch('apps.products.signals.optimize_image') as mock_opt:
            img.alt_text = 'Updated alt'
            img.sort_order = 2
            img.save()
            mock_opt.assert_not_called()

    def test_transparent_upload_remains_transparent_after_optimization(self):
        buf = io.BytesIO()
        Image.new('RGBA', (20, 20), (0, 0, 0, 0)).save(buf, format='PNG')
        image = ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile('transparent.png', buf.getvalue(), content_type='image/png'),
        )
        with image.image.open('rb') as saved:
            optimized = Image.open(saved)
            self.assertEqual(optimized.getpixel((0, 0))[3], 0)

    def test_optimization_failure_logs_warning_instead_of_silent_pass(self):
        with patch('apps.products.signals.optimize_image', side_effect=RuntimeError('corrupt image')):
            with self.assertLogs('apps.products.models', level=logging.WARNING) as cm:
                ProductImage.objects.create(
                    product=self.product,
                    image=make_test_png('bad.png'),
                )
        self.assertTrue(any('Failed to optimize product image' in msg for msg in cm.output))
