from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name='Процент начисления'
    )
    merchant_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name='Процент списания у мерчанта'
    )
    earnings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0)],
        verbose_name='Заработок'
    )
    merchant_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        verbose_name='Баланс мерчанта'
    )
    merchant_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        verbose_name='Лимит мерчанта'
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
    receipt_chat_id = models.CharField(null=True, blank=True, max_length=255, verbose_name='ID чата для чеков')
    problems_chat_id = models.CharField(null=True, blank=True, max_length=255, verbose_name='ID чата '
                                                                                            'для проблем с оплатой')
    recipients_bank = models.JSONField(null=True, blank=True, verbose_name='Банки для перевода')

    def __str__(self):
        return f"Профиль для {self.user.username}"
