from django.apps import AppConfig


class StockConfig(AppConfig):
    name = 'apps.stock'
    verbose_name = '库存管理'

    def ready(self):
        from . import signals

