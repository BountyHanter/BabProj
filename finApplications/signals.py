from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from database.models.application import Application


@receiver(post_save, sender=Application)
def application_saved(sender, instance, **kwargs):
    if instance.user_id:
        print(f"Срабатывает сигнал для пользователя {instance.user_id} с заявкой {instance.id}")
        send_update_to_user(instance.user_id, instance.id, action='update')
    else:
        print("user_id не найден для данной заявки")


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
