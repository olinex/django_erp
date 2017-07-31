from django.apps import AppConfig


class ProductConfig(AppConfig):
    name = 'apps.product'

    def ready(self):
        from . import signals
        return super(ProductConfig,self).ready()
