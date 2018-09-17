from django.apps import AppConfig


class AploaderConfig(AppConfig):
    name = 'aploader'

    def ready(self):
        from aploader import signals  # noqa
