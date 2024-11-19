import time
from datetime import datetime
from pathlib import Path

import requests
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent

def save_to_json(filename, data):
    # Если файла нет, создаем его и записываем данные
    new_data = {"average_price": data, "time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            json.dump(new_data, file, indent=4, ensure_ascii=False)
    else:
        # Если файл существует, обновляем содержимое
        with open(filename, 'r+') as file:
            try:
                file_data = json.load(file)
            except json.JSONDecodeError:
                # Если файл поврежден, записываем новые данные
                file_data = {}
            
            file_data.update(new_data)  # Обновляем существующие данные
            file.seek(0)  # Возвращаем курсор в начало файла
            file.truncate()  # Очищаем файл перед записью
            json.dump(file_data, file, indent=4, ensure_ascii=False)

def get_average_price():
    url = "https://bybit-p2p-api.p.rapidapi.com/bybit/p2p/search"

    payload = {
        "tokenId": "USDT",
        "currencyId": "RUB",
        "payment": ["582"],
        "side": "1",
        "size": "5",
        "page": "1",
        "amount": "100000",
        "authMaker": True,
        "canTrade": False
    }

    headers = {
        "x-rapidapi-key": "9336988de3msh9933fb7c280a8e7p1589e3jsnbcc819729aed",
        "x-rapidapi-host": "bybit-p2p-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()

        # Извлекаем список элементов
        items = response_data.get('result', {}).get('items', [])

        # Если нет элементов, возвращаем 0
        if not items:
            return 0

        # Собираем все цены и переводим их в float для вычислений
        prices = [float(item['price']) for item in items]

        # Суммируем цены и делим на количество элементов для вычисления среднего значения
        target_price = prices[1]

        print(target_price)

        save_to_json('average_price.json', round(target_price, 3))

    else:
        print(f"Ошибка: {response.status_code}")


def take_bybit_data():
    file_path = os.path.join(BASE_DIR, "finApplications/average_price.json")

    with open(file_path, 'r') as file:
        data = json.load(file)

    return data


if __name__ == '__main__':
    while True:
        try:
            get_average_price()
            print("Цены успешно обновлены.")
        except Exception as e:
            print(f"Ошибка: {e}")

        # Ожидание 1 минуту перед следующим запросом
        time.sleep(60)


