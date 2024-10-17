import uuid

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User, Group
from django.db import models


class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id')

    # Публичный клиентский идентификатор (например, UUID)
    client_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4)

    # Приватный клиентский секрет (хэширован)
    api_key = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Проверяем, что пользователь является мерчантом
        merchant_group = Group.objects.get(name='Merchants')
        if not self.user.groups.filter(id=merchant_group.id).exists():
            raise ValueError("API ключ может быть создан только для пользователей, принадлежащих к группе 'Merchants'.")

        # Хэшируем клиентский секрет перед сохранением
        if not self.api_key.startswith('pbkdf2'):  # Проверяем, хэширован ли секрет уже
            self.api_key = make_password(self.api_key)

        super().save(*args, **kwargs)

    def check_secret(self, raw_secret):
        # Проверяем, совпадает ли переданный клиентский секрет с хэшом
        return check_password(raw_secret, self.api_key)

    def __str__(self):
        return f"API ключ для пользователя {self.user.username}"
