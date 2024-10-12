from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from database.models.logs import log_application_action


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),

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
        permissions = [
            ('edit_processing_withdrawal', 'Права для саппорта (статус и хэш)'),
        ]

        verbose_name = "Запрос на вывод"
        verbose_name_plural = "Запросы на вывод"

    def __str__(self):
        return f"Запрос {self.id} от {self.user.username}, сумма: {self.amount}"

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из параметров
        is_new = not self.pk  # Проверяем, новый ли объект
        changed_fields = {}

        if not is_new:  # Если объект уже существует (обновление)
            old_instance = WithdrawalRequest.objects.get(pk=self.pk)
            fields_to_check = [
                'user', 'request_date', 'execution_date', 'amount', 'status', 'transaction_hash'
            ]

            for field in fields_to_check:
                old_value = getattr(old_instance, field)
                new_value = getattr(self, field)
                if old_value != new_value:
                    changed_fields[field] = {
                        'old': old_value,
                        'new': new_value
                    }

            # Проверяем, был ли статус изменён с другого на 'canceled'
            if old_instance.status != 'canceled' and self.status == 'canceled':
                # Возвращаем средства на счёт пользователя
                user_profile = self.user.profile
                user_profile.earnings += self.amount
                user_profile.save()

        # Устанавливаем время исполнения, если статус изменяется на 'completed' или 'canceled'
        if self.status in ['completed', 'canceled']:
            self.execution_date = timezone.now()

        # Вызов оригинального метода save для сохранения изменений
        super().save(*args, **kwargs)

        # Логирование изменений
        if user:
            if is_new:
                log_application_action(self, user, 'create')
            elif changed_fields:
                log_application_action(self, user, 'update', changed_fields=changed_fields)

    def delete(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user:
            log_application_action(self, user, 'delete')
        super().delete(*args, **kwargs)
