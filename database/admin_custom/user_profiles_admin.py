from django.contrib import admin
from django.contrib.auth.models import Group
from database.models.user_profile import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    fields = (
        'percentage', 'merchant_percentage', 'earnings', 'active',
        'min_amount', 'max_amount', 'problems_chat_id', 'receipt_chat_id',
        'merchant_balance', 'merchant_limit'
    )
    readonly_fields = ['earnings']

    def get_fields(self, request, obj=None):
        # Базовый набор полей для всех пользователей
        fields = [
            'percentage', 'earnings', 'active',
            'min_amount', 'max_amount', 'problems_chat_id', 'receipt_chat_id'
        ]

        # Проверка, состоит ли редактируемый пользователь в группе 'Merchants'
        user = obj.user if isinstance(obj, UserProfile) else obj
        if user and user.groups.filter(name='Merchants').exists():
            # Если пользователь в группе 'Merchants', добавляем дополнительные поля
            fields += ['merchant_percentage', 'merchant_balance', 'merchant_limit']

        return fields

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + ['earnings']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'earnings':
            kwargs['disabled'] = True
        return super().formfield_for_dbfield(db_field, request, **kwargs)
