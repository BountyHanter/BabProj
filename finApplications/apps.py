from django.apps import AppConfig


class FinApplicationsConfig(AppConfig):
    name = 'finApplications'

    def ready(self):
        print("Метод ready() вызван в FinApplicationsConfig")
        import finApplications.signals
