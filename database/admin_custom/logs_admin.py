from django.contrib import admin


class AdminActionLogAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'model_name', 'object_id', 'action', 'changes', 'timestamp']
    list_display = ['user', 'model_name', 'action', 'timestamp']

    # Переопределяем методы, чтобы запретить добавление и редактирование записей
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # Запрещаем удаление записей
    def has_delete_permission(self, request, obj=None):
        return False
