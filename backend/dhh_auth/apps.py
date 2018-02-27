from django.apps import AppConfig


class DHHAuthConfig(AppConfig):
    name = 'dhh_auth'
    verbose_name = 'DataHubHel authentication and authorization'

    def ready(self):
        import dhh_auth.signals.handlers  # noqa
