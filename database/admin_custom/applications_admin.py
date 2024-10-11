from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum, Count
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.timezone import now

from database.models.application import Application


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status', 'amount', 'created_at', 'completed_time', 'merchant_id')
    list_filter = ('status', 'type', 'created_at', 'completed_time')
    search_fields = ('from_bank', 'to_bank', 'merchant_id')
    sortable_by = ['created_at', 'completed_time', 'amount']
    ordering = ['-created_at']
    readonly_fields = ('receipt_link',)

    def get_readonly_fields(self, request, obj=None):
        """
        Определяет, какие поля будут только для чтения в зависимости от прав пользователя и состояния объекта.
        """
        # Если пользователь суперюзер, возвращаем только стандартные readonly_fields
        if request.user.is_superuser:
            return self.readonly_fields

        # Начинаем с базовых readonly_fields
        readonly_fields = list(self.readonly_fields)

        # Проверяем наличие кастомного разрешения
        if request.user.has_perm('database.edit_note_and_status'):
            if obj:
                if obj.status != 'completed':
                    # Если статус не 'completed', делаем все поля readonly, кроме 'status' и 'note'
                    editable_fields = ['status', 'note']
                    all_fields = [field.name for field in self.opts.local_fields]
                    readonly_fields += [field for field in all_fields if
                                        field not in editable_fields and field not in self.readonly_fields]
                else:
                    # Если статус 'completed', делаем все поля readonly, кроме 'note'
                    editable_fields = ['note']
                    all_fields = [field.name for field in self.opts.local_fields]
                    readonly_fields += [field for field in all_fields if
                                        field not in editable_fields and field not in self.readonly_fields]
            else:
                # Если объект не задан (например, при создании), делаем все поля readonly
                readonly_fields += [field.name for field in self.opts.local_fields if field not in self.readonly_fields]
        else:
            # Если пользователь не имеет разрешения, делаем все поля readonly
            readonly_fields += [field.name for field in self.opts.local_fields if field not in self.readonly_fields]

        return readonly_fields

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

    # Добавляем методы для форматирования дат и времени
    @admin.display(description='Дата создания', ordering='created_at')
    def formatted_created_at(self, obj):
        local_time = timezone.localtime(obj.created_at)
        return local_time.strftime('%d.%m.%Y %H:%M')

    @admin.display(description='Дата завершения', ordering='completed_time')
    def formatted_completed_time(self, obj):
        if obj.completed_time:
            local_time = timezone.localtime(obj.completed_time)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return '-'

    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

    def delete_model(self, request, obj):
        obj.delete(user=request.user)
