from django.apps import AppConfig


class WhatsappConfig(AppConfig):
    name = 'apps.whatsapp'

    def ready(self):
        import apps.whatsapp.signals  # noqa: F401
