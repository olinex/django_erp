from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'apps.account'
    verbose_name = '账号'

    def ready(self):
        from . import signals
