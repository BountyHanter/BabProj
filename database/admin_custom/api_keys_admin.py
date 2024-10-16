from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password

from database.models.api_keys import APIKey


class APIKeyInlineForm(forms.ModelForm):
    # Добавляем новое поле для ввода нового api_key
    new_api_key = forms.CharField(
        label="Новый Api-Key",
        required=False,
        widget=forms.PasswordInput,
        help_text="Введите новый Api-Key. Если оставить поле пустым, текущий секрет останется без изменений."
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

    api_key_display.short_description = "Хэшированный Api-Key"

