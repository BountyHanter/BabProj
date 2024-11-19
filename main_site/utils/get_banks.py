from django.core.cache import cache

import json
import os
from django.conf import settings  # Для работы с путями к статическим файлам


def get_banks():
    banks = cache.get('banks')
    if not banks:
        banks_json_path = os.path.join(settings.BASE_DIR, 'database', 'banks.json')
        with open(banks_json_path, 'r', encoding='utf-8') as f:
            banks = json.load(f)['dictionary']
        cache.set('banks', banks, 3600)  # Кэшируем на 1 час
    return banks


def get_bank_by_name(bank_name):
    banks = get_banks()  # Предполагаем, что get_banks() возвращает список словарей
    for bank in banks:
        if bank.get("bankName") == bank_name:
            return bank_name  # Возвращаем весь объект банка, если нужно больше данных

    return None  # Возвращаем None, если банк не найден


