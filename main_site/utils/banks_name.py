import json
import os

from finApplications import settings

banks_json_path = os.path.join(settings.BASE_DIR, 'main_site', 'banks.json')


def get_bank_names():
    try:
        with open(banks_json_path, 'r', encoding='utf-8') as f:
            banks_json = json.load(f)
            # Извлекаем список названий банков
            bank_names = [bank.get('bankName') for bank in banks_json.get('dictionary', [])]
            return bank_names
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при чтении banks.json: {e}")
        return []
