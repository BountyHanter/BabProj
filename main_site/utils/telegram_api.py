import os

import requests
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from database.models import Application

from dotenv import load_dotenv


load_dotenv()
SITE_URL = os.getenv('SITE_URL')
TG_FLASK_ADDRESS = os.getenv('TG_FLASK_ADDRESS')


def send_application_data(application_id):
    # Шаг 1: Получаем объект Application по ID
    application = get_object_or_404(Application, id=application_id)

    # Шаг 2: Извлекаем user_id и receipt_link
    user_id = application.user_id
    receipt_link = application.receipt_link
    amount = application.amount
    bank = application.bank_name

    # Шаг 3: Ищем пользователя по user_id в таблице auth_user
    user = get_object_or_404(User, id=user_id)
    username = user.username

    # Шаг 4: Отправляем POST запрос с нужными данными
    url = f"http://{TG_FLASK_ADDRESS}/api/send_application"
    data = {
        "id": application_id,
        "username": username,
        "url": f"{SITE_URL}{receipt_link}",
        "amount": float(amount),
        "bank": bank,
    }

    response = requests.post(url, json=data)

    # Логируем результат
    if response.status_code == 200:
        return True, None
    else:
        return False, f"Ошибка при отправке данных для заявки {application_id}: {response.status_code} - {response.text}"


def send_problem_data(application_id):
    # Шаг 1: Получаем объект Application по ID
    application = get_object_or_404(Application, id=application_id)

    # Шаг 2: Извлекаем user_id и receipt_link
    user_id = application.user_id
    problem = application.problem

    # Шаг 3: Ищем пользователя по user_id в таблице auth_user
    user = get_object_or_404(User, id=user_id)
    username = user.username

    # Шаг 4: Отправляем POST запрос с нужными данными
    url = f'http://{TG_FLASK_ADDRESS}/api/send_problem'
    data = {
        "id": application_id,
        "username": username,
        "problem": problem
    }

    response = requests.post(url, json=data)

    # Логируем результат
    if response.status_code == 200:
        return True, None
    else:
        return False, f"Ошибка при отправке сообщения о проблеме {application_id}: {response.status_code} - {response.text}"


def send_request_withdrawal(amount, available_amount, username):

    url = f'http://{TG_FLASK_ADDRESS}/api/request_withdrawal'
    data = {
        "amount": amount,
        "username": username,
        "available_amount": available_amount
    }

    response = requests.post(url, json=data)

    # Логируем результат
    if response.status_code == 200:
        return True, None
    else:
        return False, f"Ошибка при отправке сообщения о запросе на вывод: {response.status_code} - {response.text}"
