import json
import os

from finApplications import settings

banks_json_path = os.path.join(settings.BASE_DIR, 'database', 'banks.json')


def get_bank_names(as_choices=False):
    try:
        with open(banks_json_path, 'r', encoding='utf-8') as f:
            banks_json = json.load(f)
            bank_names = [bank.get('bankName') for bank in banks_json.get('dictionary', [])]

            # Если as_choices=True, возвращаем данные в формате для choices
            if as_choices:
                return [('', 'Все банки')] + [(name, name) for name in bank_names]

            return bank_names
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при чтении banks.json: {e}")
        return [('', 'Все банки')] if as_choices else []