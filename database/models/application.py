from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from database.models.logs import log_application_action


class ApplicationQuerySet(models.QuerySet):
    def total_created(self):
        return self.count()

    def total_completed(self):
        return self.filter(status='completed').count()

    def total_amount(self):
        result = self.aggregate(total_amount=Sum('amount'))
        return result['total_amount'] or 0


class ApplicationManager(models.Manager):
    def get_queryset(self):
        return ApplicationQuerySet(self.model, using=self._db)

    def total_created(self):
        return self.get_queryset().total_created()

    def total_completed(self):
        return self.get_queryset().total_completed()

    def total_amount(self):
        return self.get_queryset().total_amount()


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

    # Основная информация о заявке
    type = models.CharField(
        max_length=4, choices=TYPE_CHOICES, verbose_name='Тип'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='new', verbose_name='Статус'
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Сумма (в руб.)'
    )
    net_amount_in_usdt = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name='Сумма начисленная юзеру',
        null=True, blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Время создания'
    )
    taken_time = models.DateTimeField(
        null=True, blank=True, verbose_name='Время взятия'
    )
    completed_time = models.DateTimeField(
        null=True, blank=True, verbose_name='Время завершения'
    )

    # Информация о банках и реквизитах
    payment_details = models.CharField(
        max_length=255, verbose_name='Реквизиты'
    )
    to_bank = models.CharField(
        verbose_name='Банк получателя средств'
    )
    from_bank = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Банк отправителя средств'
    )

    # Ссылки и заметки
    receipt_link = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Ссылка на чек'
    )
    problem = models.CharField(
        max_length=255, verbose_name='Проблема', null=True, blank=True
    )
    note = models.CharField(
        max_length=255, verbose_name='Заметка', null=True, blank=True
    )

    # Информация о исполнителе и мерчанте
    executor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='executor_applications',
        verbose_name='Исполнитель', null=True, blank=True
    )
    merchant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='merchant_applications',
        verbose_name='Мерчант', null=True, blank=True
    )

    # Курсы и проценты
    closing_rate = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Курс на момент исполнения заявки',
        null=True, blank=True
    )
    rate_after_fee = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Курс за вычетом комиссии для команд',
        null=True, blank=True
    )
    merchant_rate_after_fee = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Курс за вычетом комиссии для мерчанта',
        null=True, blank=True
    )
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name='Процент начисления',
        null=True, blank=True
    )

    objects = ApplicationManager()

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['type']),
        ]

        permissions = [
            ('edit_note_and_status', 'Права для саппорта (заметка и статус)'),
        ]

        verbose_name = "заявку"  # Название в единственном числе
        verbose_name_plural = "Заявки"  # Название во множественном числе

    def __str__(self):
        return f"{self.id} - {self.status}"

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Получаем пользователя из параметров
        is_new = not self.pk  # Проверяем, новый ли объект
        changed_fields = {}
        old_instance = None  # Инициализируем old_instance

        if not is_new:  # Если объект уже существует (обновление)
            old_instance = Application.objects.get(pk=self.pk)
            fields_to_check = [
                'type', 'payment_details', 'to_bank', 'from_bank', 'status',
                'amount', 'net_amount_in_usdt', 'created_at', 'taken_time',
                'completed_time', 'receipt_link', 'merchant', 'executor',
                'problem', 'note'
            ]

            for field in fields_to_check:
                old_value_field = getattr(old_instance, field)
                new_value_field = getattr(self, field)
                if old_value_field != new_value_field:
                    changed_fields[field] = {
                        'old': old_value_field,
                        'new': new_value_field
                    }

        # Устанавливаем время завершения, если статус изменяется на 'completed' или 'canceled'
        if self.status in ['completed', 'canceled']:
            # Получаем старое значение completed_time из базы данных
            old_completed_time = old_instance.completed_time if old_instance else None

            if old_completed_time is None:
                if not self.completed_time:
                    self.completed_time = timezone.now()

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

