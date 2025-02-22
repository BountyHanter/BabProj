import requests

from finApplications.globals import API_URL, TG_CHAT_ID


def telegram_balance_warning(username, balance_below_zero=False):
    """Отправляет сообщение о статусе баланса пользователя в Telegram."""

    url_send_message = f"{API_URL}/sendMessage"

    text = (f'У пользователя {username} счёт ниже нуля'
            if balance_below_zero else
            f'У пользователя {username} баланс 500 USDT или менее. Пополните счёт!')

    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
    }

    response = requests.post(url_send_message, json=payload)
    check_response_status(response)


def check_response_status(response):
    """Проверяет статус ответа и выводит ошибку, если запрос не успешен."""

    if response.status_code != 200:
        print(f"Ошибка: {response.status_code}")
        try:
            print("Ответ от сервера:", response.json())  # Для JSON ответа
        except ValueError:
            print("Ответ от сервера:", response.text)  # Если ответ не в формате JSON
