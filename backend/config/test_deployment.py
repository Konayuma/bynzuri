import os
import subprocess
import sys
from unittest.mock import patch

from django.test import TestCase, override_settings


class DeploymentSettingsTests(TestCase):
    @override_settings(ALLOWED_HOSTS=['testserver'], SECURE_SSL_REDIRECT=True,
                       SECURE_REDIRECT_EXEMPT=[r'^api/health/$'])
    def test_health_checks_database_without_https_redirect_or_leaking_errors(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        with patch('config.urls.connection.cursor', side_effect=Exception('private database details')):
            response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private database details', response.content.decode())

    def test_neon_and_r2_configuration(self):
        env = os.environ.copy()
        env.update({
            'DJANGO_SETTINGS_MODULE': 'config.settings', 'DJANGO_DEBUG': 'False',
            'DJANGO_SECRET_KEY': 'deployment-test-key-abcdefghijklmnopqrstuvwxyz-0123456789',
            'DATABASE_URL': 'postgresql://test:test@db.example/test?sslmode=require&channel_binding=require',
            'RENDER_EXTERNAL_HOSTNAME': 'api.example.com', 'REQUIRE_PERSISTENT_MEDIA': 'true',
            'R2_ACCESS_KEY_ID': 'test', 'R2_SECRET_ACCESS_KEY': 'test', 'R2_BUCKET_NAME': 'test',
            'R2_ENDPOINT_URL': 'https://example.r2.cloudflarestorage.com', 'R2_PUBLIC_DOMAIN': 'media.example.com',
        })
        env.pop('USE_SQLITE', None)
        script = """import django; django.setup()
from django.conf import settings
from django.core.files.storage import storages
assert settings.DATABASES['default']['OPTIONS']['sslmode'] == 'require'
assert settings.DATABASES['default']['OPTIONS']['channel_binding'] == 'require'
assert 'api.example.com' in settings.ALLOWED_HOSTS
assert storages['default'].url('products/item.png') == 'https://media.example.com/products/item.png'
"""
        subprocess.run([sys.executable, '-c', script], env=env, check=True, capture_output=True, text=True)
