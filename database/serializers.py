import json
import os
import re

from rest_framework import serializers

from database.models.application import Application
from finApplications.settings import BASE_DIR

# Полный путь к файлу banks.json
file_path = os.path.join(BASE_DIR, 'main_site/banks.json')

# Загрузим данные из banks.json
with open(file_path, 'r', encoding='utf-8') as f:
    BANKS = json.load(f).get('dictionary', [])


class ApplicationSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField(required=True)  # Тип — число, обязательно
    payment_details = serializers.CharField(required=True)  # Реквизиты, обязательны
    to_bank = serializers.CharField(required=False)  # Имя банка, не обязателен
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Сумма — число, обязательно
    bank_id = serializers.CharField(write_only=True, required=True)  # ID банка, обязателен, но не сохраняется

    class Meta:
        model = Application
        fields = ['type', 'payment_details', 'to_bank', 'amount', 'bank_id']

    def validate_type(self, value):
        # Проверка значения type (1 или 2) и преобразование его в строку
        if value not in [1, 2]:
            raise serializers.ValidationError("Поле 'type' должно быть либо 1 (C2C), либо 2 (SBP).")
        return "c2c" if value == 1 else "sbp"

    def validate(self, data):
        """
        Общая валидация и форматирование полей на основе типа платежа.
        """
        type_value = data.get('type')
        payment_details = data.get('payment_details')
        bank_id = data.get('bank_id')  # Получаем переданный bank_id из запроса

        # Проверка, что bank_id является строкой и соответствует формату
        if not isinstance(bank_id, str) or not bank_id.startswith('bank') or not bank_id[4:].isdigit():
            raise serializers.ValidationError({
                "bank_id": "Некорректный формат bank_id. Ожидается строка, начинающаяся с 'bank' и за которой следуют цифры."
            })

        # Поиск банка по schema
        bank = next((b for b in BANKS if b['schema'] == bank_id), None)
        if not bank:
            raise serializers.ValidationError({
                "bank_id": f"Банк с ID {bank_id} не найден."
            })

        # Присваиваем имя банка в поле user_bank
        data['to_bank'] = bank['bankName']

        # Валидация и форматирование реквизитов платежа
        if type_value == "sbp":  # SBP
            digits = payment_details.lstrip('+')
            if not re.fullmatch(r'7\d{10}', digits):
                raise serializers.ValidationError({
                    "payment_details": "Для SBP платежей 'payment_details' должно быть номером телефона."
                })
            formatted_phone = f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
            data['payment_details'] = formatted_phone

        elif type_value == "c2c":  # C2C
            digits = payment_details.lstrip('+')
            if not digits.isdigit() or len(digits) <= 11:
                raise serializers.ValidationError({
                    "payment_details": "Для C2C платежей 'payment_details' должно быть номером карты более 11 цифр."
                })
            formatted_card = ' '.join([digits[i:i + 4] for i in range(0, len(digits), 4)])
            data['payment_details'] = formatted_card

        return data

    def create(self, validated_data):
        # Удаляем bank_id, чтобы оно не сохранялось
        validated_data.pop('bank_id', None)

        # Устанавливаем статус по умолчанию
        validated_data['status'] = 'new'

        return Application.objects.create(**validated_data)