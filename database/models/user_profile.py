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
