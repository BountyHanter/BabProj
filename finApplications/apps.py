from django.apps import AppConfig


class FinApplicationsConfig(AppConfig):
    name = 'finApplications'

    def ready(self):
        import finApplications.signals  # Подключение
