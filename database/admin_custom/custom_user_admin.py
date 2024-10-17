from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from database.admin_custom.api_keys_admin import APIKeyInline
from database.admin_custom.user_profiles_admin import UserProfileInline
from database.models.api_keys import APIKey


class CustomUserAdmin(UserAdmin):
    inlines = (APIKeyInline, UserProfileInline,)  # Добавляем UserProfileInline

    list_display = ('username', 'get_groups') + UserAdmin.list_display[1:] + ('get_percentage', 'get_earnings',)
    list_select_related = ('profile',)  # Оптимизирует запросы для связанных моделей

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Группы'  # Название столбца в админке

    def get_percentage(self, obj):
        return obj.profile.percentage

    get_percentage.short_description = 'Процент начисления'
    get_percentage.admin_order_field = 'profile__percentage'

    def get_earnings(self, obj):
        return obj.profile.earnings

    get_earnings.short_description = 'Заработок'
    get_earnings.admin_order_field = 'profile__earnings'

    def save_model(self, request, obj, form, change):
        # Сначала сохраняем объект пользователя
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == APIKey:
            instances = formset.save(commit=False)

            for instance in instances:
                # Проверяем, был ли введен новый API ключ
                new_api_key = formset.forms[0].cleaned_data.get('new_api_key', None)

                # Если новый API ключ не введен, пропускаем сохранение
                if not new_api_key:
                    continue

                # Проверяем, состоит ли пользователь в группе 'Merchants'
                merchant_group = Group.objects.get(name='Merchants')
                if not instance.user.groups.filter(id=merchant_group.id).exists():
                    # Добавляем сообщение об ошибке и не сохраняем APIKey
                    messages.error(request,
                                   "API ключ может быть создан только для пользователей, принадлежащих к группе 'Merchants'.")
                    continue  # Пропускаем сохранение этого инстанса

                # Сохраняем API ключ только если все условия выполнены
                instance.save()

            # Сохраняем m2m данные после сохранения инстансов
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)
