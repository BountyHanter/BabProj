from django.apps import AppConfig
from django.db.models.signals import post_migrate


class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'

    def ready(self):
        # Импортируем здесь, чтобы избежать проблем с инициализацией приложений
        from django.contrib.auth.models import Group
        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    groups = ['Merchants']  # Список групп для создания
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Группа {group_name} создана")
