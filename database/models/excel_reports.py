from django.db import models
from django.contrib.auth.models import User


class Report(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, запросивший отчёт'
    )
    report_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отчёта'
    )
    report_link = models.URLField(
        max_length=255,
        verbose_name='Ссылка на отчёт'
    )
    application_count = models.PositiveIntegerField(
        verbose_name='Количество заявок в отчёте'
    )

    class Meta:
        verbose_name = 'Запрошенный отчёт'
        verbose_name_plural = 'Запрошенные отчёты'
        ordering = ['-report_date']

        permissions = [
            ('can_view_all_reports', 'Может получить отчёт со всеми данными всех пользователей'),
        ]

    def __str__(self):
        return f"Отчёт #{self.id} от {self.user}"