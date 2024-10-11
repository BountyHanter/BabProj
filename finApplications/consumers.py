from channels.generic.websocket import AsyncWebsocketConsumer
import json


class DatabaseUpdateConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None  # Инициализируем group_name

    async def connect(self):
        # # Выводим информацию о сессии и пользователе
        if self.scope['user'].is_authenticated:
            print(f"Authenticated user: {self.scope['user'].id}")
        else:
            print("User is not authenticated")

        user = self.scope['user']

        if user.is_authenticated:
            user_id = user.id
            self.group_name = f"user_{user_id}"

            print(f"Пользователь {user_id} подключен. Группа: {self.group_name}")

            # Добавляем пользователя в его личную группу
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            # Подтверждаем соединение
            await self.accept()
        else:
            print("Неаутентифицированный пользователь пытается подключиться.")
            await self.close()

    async def disconnect(self, close_code):
        # Проверяем, что group_name существует перед тем, как его использовать
        if self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"Пользователь {self.scope['user'].id} отключился от группы {self.group_name}")
        else:
            print("Попытка отключения без group_name")

    # Метод для отправки сообщений пользователю
    async def send_update(self, event):
        if self.group_name:
            action = event.get('action', 'update')  # Получаем действие из event, по умолчанию 'update'
            application_id = event.get('application_id')

            print(
                f"Отправляем сообщение пользователю {self.scope['user'].id} в группе {self.group_name} с действием {action}")

            await self.send(text_data=json.dumps({
                'action': action,  # Используем переданное действие
                'application_id': application_id
            }))
            print(f"Отправлено сообщение пользователю: action={action}, application_id={application_id}")
