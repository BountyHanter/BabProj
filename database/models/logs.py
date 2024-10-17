from django.contrib.auth.models import User
from django.db import models


class AdminActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    model_name = models.CharField(max_length=50, verbose_name='Модель')
    object_id = models.PositiveIntegerField(verbose_name='ID объекта')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='Действие')
    changes = models.TextField(null=True, blank=True, verbose_name='Изменения')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')

    def __str__(self):
        return f"{self.user} - {self.model_name} - {self.action} - {self.timestamp}"

    class Meta:
        verbose_name = "Лог действия"
        verbose_name_plural = "Логи действий"
        ordering = ['-timestamp']


def log_application_action(instance, user, action, changed_fields=None):
    if action == 'create':
        changes_text = f"Создан объект с ID {instance.pk}"
    elif action == 'delete':
        changes_text = f"Удалён объект с ID {instance.pk}"
    elif changed_fields:
        changes = []
        for field, values in changed_fields.items():
            change_description = f"Поле '{field}': было '{values['old']}', стало '{values['new']}'"
            changes.append(change_description)
        changes_text = "; ".join(changes)
    else:
        changes_text = None

    AdminActionLog.objects.create(
        user=user,
        model_name=instance.__class__.__name__,
        object_id=instance.pk,
        action=action,
        changes=changes_text,
    )
