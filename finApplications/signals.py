from django.db.models.signals import post_save, pre_save
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
    if instance.executor:
        # Проверяем, изменился ли статус
        if hasattr(instance, '_original_status') and instance.status != instance._original_status:
            print(f"Срабатывает сигнал для пользователя {instance.executor} с заявкой {instance.id}")
            action = instance.status
            send_update_to_user(instance.executor, instance.id, action=action)


def send_update_to_user(user_id, application_id, action='update'):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_update",
            "action": action,
            "application_id": application_id
        }
    )
    print(f"Отправлен сигнал пользователю {user_id} о заявке {application_id} с действием {action}")
