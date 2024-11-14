import json

from django.contrib import admin
from django import forms

from database.admin_custom.widget import BankSelectionWidget
from database.models.user_profile import UserProfile


# Кастомная форма админки для UserProfile
class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'

    recipients_bank = forms.Field(
        required=False,
        label='Банки для перевода',
        widget=BankSelectionWidget()
    )

    def clean_recipients_bank(self):
        data = self.cleaned_data.get('recipients_bank')
        if data:
            if isinstance(data, list):
                bank_list = data
            elif isinstance(data, str):
                try:
                    bank_list = json.loads(data)
                except json.JSONDecodeError:
                    raise forms.ValidationError("Некорректный формат данных для банков")
            else:
                raise forms.ValidationError("Некорректный тип данных для банков")
            return bank_list
        return []


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    form = UserProfileAdminForm  # Подключаем кастомную форму
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
            'min_amount', 'max_amount', 'problems_chat_id', 'receipt_chat_id', 'recipients_bank'
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

    def save_model(self, request, obj, form, change):
        print('Вызов')
        # Получаем значение из cleaned_data формы
        recipients_bank = form.cleaned_data.get('recipients_bank')
        if recipients_bank is not None:
            print(recipients_bank)
            obj.recipients_bank = recipients_bank

        # Сохраняем объект
        super().save_model(request, obj, form, change)
