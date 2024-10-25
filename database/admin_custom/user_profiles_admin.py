from django.contrib import admin

from database.models.user_profile import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    fields = ('percentage', 'merchant_percentage', 'earnings', 'active', 'min_amount', 'max_amount', 'problems_chat_id', 'receipt_chat_id',
              'merchant_balance', 'merchant_limit')
    readonly_fields = ['earnings', ]  # Если хотите сделать поле только для чтения, добавьте сюда

    def get_readonly_fields(self, request, obj=None):
        # Убедимся, что возвращаем список строк
        return list(self.readonly_fields) + ['earnings']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Проверяем, если поле - "earnings", то делаем его только для чтения
        if db_field.name == 'earnings':
            kwargs['disabled'] = True
        return super().formfield_for_dbfield(db_field, request, **kwargs)