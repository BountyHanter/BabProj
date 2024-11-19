from django.contrib import admin
from django.utils.html import format_html
import os


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report_date', 'application_count', 'clickable_report_link')
    list_filter = ('report_date', 'user')
    search_fields = ('user__username', 'report_link')

    # Опционально, можно добавить дополнительные настройки
    ordering = ('-report_date',)

    readonly_fields = ('clickable_report_link',)

    # Добавляем метод для отображения кликабельной ссылки на отчет
    def clickable_report_link(self, obj):
        if obj.report_link:
            domain = os.getenv('SITE_URL')
            full_url = f"{domain}{obj.report_link}"
            return format_html(f'<a href="{full_url}" target="_blank">{full_url}</a>')
        return "Нет отчета"

    clickable_report_link.short_description = "Ссылка на отчет"

    # Переопределяем методы, чтобы запретить добавление и редактирование записей
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # Запрещаем удаление записей
    def has_delete_permission(self, request, obj=None):
        return False
