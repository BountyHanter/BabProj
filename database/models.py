from django.contrib.auth.models import User, Group
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator


class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('active', 'Active'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('manual', 'Manual'),
    ]

    TYPE_CHOICES = [
        ('c2c', 'C2C'),
        ('sbp', 'SBP')
    ]

    type = models.CharField(max_length=4, choices=TYPE_CHOICES, verbose_name='Тип')
    payment_details = models.CharField(max_length=255, verbose_name='Реквизиты')
    bank_id = models.IntegerField(null=True, blank=True, verbose_name='ID Банка')
    bank_name = models.CharField(max_length=255, verbose_name='Название банка')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма (в руб.)')
    net_amount_in_usdt = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма начисленная юзеру', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    taken_time = models.DateTimeField(null=True, blank=True, verbose_name='Время взятия')
    completed_time = models.DateTimeField(null=True, blank=True, verbose_name='Время завершения')
    receipt_link = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ссылка на чек')
    merchant_id = models.IntegerField(verbose_name='ID Мерчанта')
    user_id = models.IntegerField(verbose_name='ID Юзера', null=True, blank=True)
    customer = models.CharField(max_length=255, verbose_name='Покупатель', null=True, blank=True, unique=True)
    problem = models.CharField(max_length=255, verbose_name='Проблема', null=True, blank=True)
    note = models.CharField(max_length=255, verbose_name='Заметка', null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['type']),
        ]

        verbose_name = "заявку"  # Название в единственном числе
        verbose_name_plural = "Заявки"  # Название во множественном числе

    def __str__(self):
        return f"{self.id} - {self.status}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests',
                             verbose_name='Пользователь')
    request_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания запроса')
    execution_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата исполнения запроса')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма запроса (в USDT)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='processing',
                              verbose_name='Статус запроса')
    transaction_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name='Хэш транзакции')

    class Meta:

        verbose_name = "Запрос на вывод"
        verbose_name_plural = "Запросы на вывод"

    def __str__(self):
        return f"Запрос {self.id} от {self.user.username}, сумма: {self.amount}"


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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name='Процент начисления'
    )
    earnings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name='Заработок'
    )
    min_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name='Минимальная сумма заявки'
    )
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        verbose_name='Максимальная сумма заявки'
    )
    active = models.BooleanField(default=True, verbose_name='Возможность обрабатывать заявки')

    def __str__(self):
        return f"Профиль для {self.user.username}"


# Сигналы для автоматического создания и сохранения профиля пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
