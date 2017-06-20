from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = 'account'

    def ready(self):
        from . import signals
        return super(AccountConfig,self).ready()
