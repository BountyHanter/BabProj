from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.urls import path
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils.timezone import now
from django.template.response import TemplateResponse
from datetime import timedelta
from django.contrib import admin

from .models import Application, UserProfile, WithdrawalRequest
from .models import APIKey


# Админка для модели Application
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status', 'amount', 'created_at', 'completed_time', 'merchant_id', 'customer')
    list_filter = ('status', 'type', 'created_at', 'completed_time')  # Добавляем кастомный фильтр
    search_fields = ('bank_name', 'customer', 'merchant_id')
    sortable_by = ['created_at', 'completed_time', 'amount']
    ordering = ['-created_at']

    # Функция для отображения страницы статистики
    def statistics_view(self, request):
        today = now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)

        # Статистика по количеству заявок
        stats = {
            'total_count': Application.objects.count(),
            'count_day': Application.objects.filter(created_at__gte=today).count(),
            'count_week': Application.objects.filter(created_at__gte=week_ago).count(),
            'count_month': Application.objects.filter(created_at__gte=month_ago).count(),
            'count_year': Application.objects.filter(created_at__gte=year_ago).count(),

            # Сумма заявок
            'total_sum': Application.objects.aggregate(total=Sum('amount'))['total'] or 0,
            'sum_day': Application.objects.filter(created_at__gte=today).aggregate(total=Sum('amount'))['total'] or 0,
            'sum_week': Application.objects.filter(created_at__gte=week_ago).aggregate(total=Sum('amount'))[
                            'total'] or 0,
            'sum_month': Application.objects.filter(created_at__gte=month_ago).aggregate(total=Sum('amount'))[
                             'total'] or 0,
            'sum_year': Application.objects.filter(created_at__gte=year_ago).aggregate(total=Sum('amount'))[
                            'total'] or 0,
        }

        # Статистика по мерчантам
        merchants = Application.objects.values('merchant_id').annotate(
            total_count=Count('id'),
            total_sum=Sum('amount')
        ).order_by('-total_count')

        context = {
            **self.admin_site.each_context(request),
            'stats': stats,
            'merchants': merchants,
        }

        return TemplateResponse(request, 'admin/application_statistics.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='application_statistics'),
        ]
        return custom_urls + urls


class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'request_date', 'execution_date')
    list_filter = ('status', 'request_date')  # Фильтры по статусу и дате запроса
    search_fields = ('user__username', 'transaction_hash')  # Поля для поиска

    # Добавляем поле request_date как только для чтения
    readonly_fields = ('request_date', 'amount', 'user')

    # (Опционально) Определяем поля формы, включая request_date
    # Если вы не используете пользовательские формы или fieldsets, этот шаг не обязателен
    fields = ('user', 'request_date', 'execution_date', 'amount', 'status', 'transaction_hash')


admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(Application, ApplicationAdmin)


class APIKeyInlineForm(forms.ModelForm):
    # Добавляем новое поле для ввода нового api_key
    new_api_key = forms.CharField(
        label="Новый Client Secret",
        required=False,
        widget=forms.PasswordInput,
        help_text="Введите новый Client Secret. Если оставить поле пустым, текущий секрет останется без изменений."
    )

    class Meta:
        model = APIKey
        fields = ['client_id']

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Если введён новый клиентский секрет, хэшируем его
        new_secret = self.cleaned_data.get('new_api_key')
        if new_secret:
            instance.api_key = make_password(new_secret)

        if commit:
            instance.save()
        return instance


class APIKeyInline(admin.StackedInline):
    model = APIKey
    form = APIKeyInlineForm
    can_delete = False
    verbose_name_plural = 'API Keys'
    readonly_fields = ('client_id', 'api_key_display')  # Показываем client_id и api_key как подписи
    fields = ('client_id', 'new_api_key', 'api_key_display')  # Поле для ввода нового ключа

    def api_key_display(self, obj):
        return obj.api_key if obj.api_key else "Нет ключа"

    api_key_display.short_description = "Хэшированный Client Secret"


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    fields = ('percentage', 'earnings', 'active', 'min_amount', 'max'
                                                                '_amount')  # Добавляем поле earnings
    readonly_fields = ()  # Если хотите сделать поле только для чтения, добавьте сюда


# Обновление CustomUserAdmin для включения APIKeyInline и UserProfileInline
class CustomUserAdmin(UserAdmin):
    inlines = (APIKeyInline, UserProfileInline,)  # Добавляем UserProfileInline

    list_display = UserAdmin.list_display + ('get_percentage', 'get_earnings',)
    list_select_related = ('profile',)  # Оптимизирует запросы для связанных моделей

    def get_percentage(self, obj):
        return obj.profile.percentage
    get_percentage.short_description = 'Процент начисления'
    get_percentage.admin_order_field = 'profile__percentage'

    def get_earnings(self, obj):
        return obj.profile.earnings
    get_earnings.short_description = 'Заработок'
    get_earnings.admin_order_field = 'profile__earnings'

    def save_model(self, request, obj, form, change):
        # Сначала сохраняем объект пользователя
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == APIKey:
            instances = formset.save(commit=False)

            for instance in instances:
                # Проверяем, был ли введен новый API ключ
                new_api_key = formset.forms[0].cleaned_data.get('new_api_key', None)

                # Если новый API ключ не введен, пропускаем сохранение
                if not new_api_key:
                    continue

                # Проверяем, состоит ли пользователь в группе 'Merchants'
                merchant_group = Group.objects.get(name='Merchants')
                if not instance.user.groups.filter(id=merchant_group.id).exists():
                    # Добавляем сообщение об ошибке и не сохраняем APIKey
                    messages.error(request, "API ключ может быть создан только для пользователей, принадлежащих к группе 'Merchants'.")
                    continue  # Пропускаем сохранение этого инстанса

                # Сохраняем API ключ только если все условия выполнены
                instance.save()

            # Сохраняем m2m данные после сохранения инстансов
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)


# Перерегистрируем модель пользователя с обновленной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

