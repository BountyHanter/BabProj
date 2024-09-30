import json
import os
import re

from rest_framework import serializers
from .models import Application

from rest_framework.exceptions import ValidationError



# Получаем путь к директории, где находится текущий файл (serializers.py)
current_dir = os.path.dirname(__file__)

# Полный путь к файлу banks.json
file_path = os.path.join(current_dir, '../main_site/banks.json')

# Загрузим данные из banks.json
with open(file_path, 'r', encoding='utf-8') as f:
    BANKS = json.load(f)


class ApplicationSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=True)  # Тип — число, обязательно
    payment_details = serializers.CharField(required=True)  # Реквизиты, обязательны
    bank_id = serializers.IntegerField(required=False)  # ID банка, обязателен только для C2C
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Сумма — число, обязательно

    class Meta:
        model = Application
        fields = ['type', 'payment_details', 'bank_id', 'amount']

    def to_internal_value(self, data):
        # Получаем список полей, которые мы разрешаем
        allowed_fields = set(self.fields.keys())
        incoming_fields = set(data.keys())

        # Проверяем, есть ли какие-то неизвестные поля
        extra_fields = incoming_fields - allowed_fields
        if extra_fields:
            raise ValidationError({
                "extra_fields": f"Поля {', '.join(extra_fields)} не разрешены."
            })

        return super().to_internal_value(data)

    def validate_type(self, value):
        # Проверка значения type (1 или 2)
        if value not in [1, 2]:
            raise serializers.ValidationError("Поле 'type' должно быть либо 1 (C2C), либо 2 (SBP).")
        return "c2c" if value == 1 else "sbp"

    def validate(self, data):
        """
        Общая валидация и форматирование полей на основе типа платежа.
        """
        type_value = data.get('type')  # Уже преобразовано в 'c2c' или 'sbp'
        payment_details = data.get('payment_details')
        bank_id = data.get('bank_id')

        if type_value == 'c2c':
            if bank_id is None:
                raise serializers.ValidationError({
                    "bank_id": "Поле 'bank_id' обязательно для платежей типа C2C."
                })
        elif type_value == 'sbp':
            if bank_id is not None:
                raise serializers.ValidationError({
                    "bank_id": "Поле 'bank_id' не должно присутствовать для платежей типа SBP."
                })
        else:
            raise serializers.ValidationError({
                "type": f"Неизвестный тип платежа: {type_value}."
            })

        # Валидация и форматирование payment_details
        if not type_value or not payment_details:
            return data  # Дополнительные ошибки будут обработаны отдельно

        if type_value == 'sbp':
            digits = payment_details.lstrip('+')  # Удаляем возможный ведущий '+'

            if not re.fullmatch(r'7\d{10}', digits):
                raise serializers.ValidationError({
                    "payment_details": "Для платежей типа SBP поле 'payment_details' должно быть номером телефона из 11 цифр, начинающимся с '7'."
                })

            formatted_phone = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
            data['payment_details'] = formatted_phone

        elif type_value == 'c2c':
            digits = payment_details.lstrip('+')  # Удаляем возможный ведущий '+'

            if not digits.isdigit():
                raise serializers.ValidationError({
                    "payment_details": "Поле 'payment_details' должно содержать только цифры."
                })

            if len(digits) <= 11:
                raise serializers.ValidationError({
                    "payment_details": "Для платежей типа C2C поле 'payment_details' должно быть номером карты более 11 цифр."
                })

            formatted_card = ' '.join([digits[i:i+4] for i in range(0, len(digits), 4)])
            data['payment_details'] = formatted_card

        return data

    def create(self, validated_data):
        # Устанавливаем статус по умолчанию
        validated_data['status'] = 'new'

        # merchant_id будет назначен в представлении
        return Application.objects.create(**validated_data)
