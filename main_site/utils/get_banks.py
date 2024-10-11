from django.core.cache import cache

import json
import os
from django.conf import settings  # Для работы с путями к статическим файлам


def get_banks():
    banks = cache.get('banks')
    if not banks:
        banks_json_path = os.path.join(settings.BASE_DIR, 'main_site', 'banks.json')
        with open(banks_json_path, 'r', encoding='utf-8') as f:
            banks = json.load(f)['dictionary']
        cache.set('banks', banks, 3600)  # Кэшируем на 1 час
    return banks


def get_bank_name_by_index(bank_id):
    banks = get_banks()
    try:
        # Индекс начинается с 1, поэтому вычитаем 1 для корректного доступа
        bank = banks[int(bank_id) - 1]
        return bank.get('bankName')
    except (IndexError, ValueError):
        # Если индекс выходит за пределы или не является числом
        return None
