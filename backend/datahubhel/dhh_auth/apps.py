from django.apps import AppConfig


class DHHAuthConfig(AppConfig):
    name = 'datahubhel.dhh_auth'
    verbose_name = 'DataHubHel authentication and authorization'

    def ready(self):
        import datahubhel.dhh_auth.signals.handlers  # noqa
