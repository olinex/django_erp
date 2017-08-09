from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'apps.product'
    verbose_name = '产品'

    def ready(self):
        from . import signals
