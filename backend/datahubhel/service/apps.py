from django.apps import AppConfig


class ServiceConfig(AppConfig):
    name = 'datahubhel.service'
    verbose_name = 'DataHubHel Service'

    def ready(self):
        import datahubhel.service.signals.handlers  # noqa
