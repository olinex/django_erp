from django.apps import AppConfig


class StockConfig(AppConfig):
    name = 'stock'

    def ready(self):
        from . import signals
        return super(StockConfig,self).ready()
