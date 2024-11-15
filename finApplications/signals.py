from django.db.models.signals import post_save, pre_save
from django.db import transaction
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from database.models.application import Application

# Предварительное сохранение для отслеживания изменений
@receiver(pre_save, sender=Application)
def application_pre_save(sender, instance, **kwargs):
    if instance.pk:
        # Сохраняем предыдущее значение статуса
        instance._original_status = Application.objects.get(pk=instance.pk).status
    else:
        instance._original_status = None

@receiver(post_save, sender=Application)
def application_saved(sender, instance, **kwargs):
    if instance.executor:  # Убедитесь, что executor существует
        if hasattr(instance, '_original_status') and instance.status != instance._original_status:
            print(f"Срабатывает сигнал для пользователя {instance.executor} с заявкой {instance.id}")
            action = instance.status

            # Используем transaction.on_commit, чтобы отправить сообщение после фиксации транзакции
            transaction.on_commit(lambda: send_update_to_user(instance.executor.id, instance.id, action=action))


def send_update_to_user(user_id, application_id, action='update'):
    group_name = f"user_{user_id}"
    print(f"[DEBUG] Отправляем сообщение в группу {group_name} с action={action}, application_id={application_id}")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_update",
            "action": action,
            "application_id": application_id
        }
    )
