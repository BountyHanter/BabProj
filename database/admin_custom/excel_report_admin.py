from django.contrib import admin


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report_date', 'application_count')
    list_filter = ('report_date', 'user')
    search_fields = ('user__username', 'report_link')

    # Опционально, можно добавить дополнительные настройки
    ordering = ('-report_date',)

    # Переопределяем методы, чтобы запретить добавление и редактирование записей
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # Запрещаем удаление записей
    def has_delete_permission(self, request, obj=None):
        return False
