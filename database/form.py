from django import forms
from .models import APIKey
from django.contrib.auth.hashers import make_password

class APIKeyAdminForm(forms.ModelForm):
    new_api_key = forms.CharField(
        label="Новый Client Secret",
        required=False,
        widget=forms.PasswordInput,
        help_text="Введите новый Client Secret. Если поле пустое, текущий секрет останется без изменений."
    )

    class Meta:
        model = APIKey
        fields = ['client_id']  # Показываем только client_id, а api_key не редактируем

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Если введён новый клиентский секрет, хэшируем и сохраняем его
        new_secret = self.cleaned_data.get('new_api_key')
        if new_secret:
            instance.api_key = make_password(new_secret)

        if commit:
            instance.save()
        return instance
