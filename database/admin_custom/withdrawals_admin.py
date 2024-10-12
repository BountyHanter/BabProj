from django.contrib import admin
from django.utils import timezone


class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'formatted_request_date', 'formatted_execution_time')
    list_filter = ('status', 'request_date')  # Фильтры по статусу и дате запроса
    search_fields = ('user__username', 'transaction_hash')  # Поля для поиска

    # Добавляем поле request_date как только для чтения
    readonly_fields = ('request_date', 'amount', 'user')

    # (Опционально) Определяем поля формы, включая request_date
    # Если вы не используете пользовательские формы или fieldsets, этот шаг не обязателен
    fields = ('user', 'request_date', 'execution_date', 'amount', 'status', 'transaction_hash')

    # Добавляем методы для форматирования дат и времени
    @admin.display(description='Дата создания', ordering='request_date')
    def formatted_request_date(self, obj):
        local_time = timezone.localtime(obj.request_date)
        return local_time.strftime('%d.%m.%Y %H:%M')

    @admin.display(description='Дата исполнения', ordering='execution_date')
    def formatted_execution_time(self, obj):
        if obj.execution_date:
            local_time = timezone.localtime(obj.execution_date)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return '-'

    def get_readonly_fields(self, request, obj=None):
        # Если пользователь суперюзер, возвращаем только стандартные readonly_fields
        if request.user.is_superuser:
            return self.readonly_fields

        # Начинаем с базовых readonly_fields
        readonly_fields = list(self.readonly_fields)

        # Если объект существует и его статус 'completed' или 'canceled', делаем все поля readonly
        if obj and obj.status in ['completed', 'canceled']:
            all_fields = [field.name for field in self.opts.local_fields]
            readonly_fields += [field for field in all_fields if field not in self.readonly_fields]
        else:
            # Проверяем наличие кастомного разрешения
            if request.user.has_perm('database.edit_processing_withdrawal'):
                if obj and obj.status == 'processing':
                    # Разрешаем редактировать только 'status' и 'transaction_hash'
                    editable_fields = ['status', 'transaction_hash']
                    all_fields = [field.name for field in self.opts.local_fields]
                    readonly_fields += [field for field in all_fields if
                                        field not in editable_fields and field not in self.readonly_fields]
                else:
                    # Если статус не 'processing', делаем все поля readonly
                    all_fields = [field.name for field in self.opts.local_fields]
                    readonly_fields += [field for field in all_fields if field not in self.readonly_fields]
            else:
                # Если пользователь не имеет разрешения, делаем все поля readonly
                all_fields = [field.name for field in self.opts.local_fields]
                readonly_fields += [field for field in all_fields if field not in self.readonly_fields]

        return readonly_fields

    def save_model(self, request, obj, form, change):
        # Передаём текущего пользователя в метод save модели
        obj.save(user=request.user)

    def delete_model(self, request, obj):
        # Передаём текущего пользователя в метод delete модели
        obj.delete(user=request.user)
