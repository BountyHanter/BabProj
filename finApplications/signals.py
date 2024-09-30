from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from database.models import Application


def send_update_to_user(user_id, application_id, action='update'):
    try:
        # Получаем слой каналов
        channel_layer = get_channel_layer()

        # Отправляем сообщение в группу пользователя
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",  # Группа, с которой связан пользователь
            {
                "type": "send_update",  # Название обработчика события в Consumer
                "action": action,       # Тип действия: 'update' или 'cancel'
                "application_id": application_id  # Данные для отправки
            }
        )
        print(f"Отправлен сигнал пользователю {user_id} о заявке {application_id} с действием {action}")
    except Exception as e:
        print(f"Ошибка при отправке сигнала: {str(e)}")

