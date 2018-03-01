from django.apps import AppConfig


class ServiceConfig(AppConfig):
    name = 'service'
    verbose_name = 'DataHubHel Service'

    def ready(self):
        import service.signals.handlers  # noqa
