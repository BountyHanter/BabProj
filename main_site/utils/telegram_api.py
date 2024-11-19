import requests
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from database.models import UserProfile
from database.models.application import Application
from finApplications.globals import TG_FLASK_ADDRESS, SITE_URL


def send_application_data(application_id):
    # Шаг 1: Получаем объект Application по ID
    application = get_object_or_404(Application, id=application_id)

    # Шаг 2: Извлекаем данные из заявки
    user_id = application.executor.id
    receipt_link = application.receipt_link
    amount = application.amount
    from_bank = application.from_bank
    to_bank = application.to_bank

    # Шаг 3: Ищем пользователя по user_id в таблице auth_user
    user = get_object_or_404(User, id=user_id)
    username = user.username

    # Шаг 4: Получаем профиль пользователя
    user_profile = get_object_or_404(UserProfile, user=user)

    # Извлекаем ID чата для чеков
    receipt_chat_id = user_profile.receipt_chat_id

    # Шаг 5: Отправляем POST запрос с нужными данными
    url = f"http://{TG_FLASK_ADDRESS}/api/send_application"
    data = {
        "id": application_id,
        "username": username,
        "url": f"{SITE_URL}{receipt_link}",
        "amount": float(amount),
        "from_bank": from_bank,
        "to_bank": to_bank,
        "receipt_chat_id": receipt_chat_id  # Добавляем поле receipt_chat_id
    }
    response = requests.post(url, json=data)

    # Логируем результат
    if response.status_code == 200:
        # Предполагаем, что API возвращает JSON-ответ, который можно проверить
        response_data = response.json()
        if response_data.get("status") == "success":
            return True, None
        else:
            # Возвращаем ошибки, если статус не "success"
            errors = response_data.get("errors", [])
            return False, f"Ошибка при отправке данных: {errors}"
    else:
        # Если запрос не успешен, возвращаем статус код и текст ответа
        return False, f"Ошибка при отправке сообщения о проблеме {application_id}: {response.status_code} - {response.text}"


def send_problem_data(application_id):
    # Шаг 1: Получаем объект Application по ID
    application = get_object_or_404(Application, id=application_id)

    # Шаг 2: Извлекаем user_id и problem
    user_id = application.executor.id  # Извлекаем ID пользователя из объекта User
    problem = application.problem

    # Шаг 3: Ищем пользователя по user_id в таблице auth_user
    user = get_object_or_404(User, id=user_id)
    username = user.username

    # Шаг 4: Получаем профиль пользователя
    user_profile = get_object_or_404(UserProfile, user=user)

    # Извлекаем ID чата для проблем
    problems_chat_id = user_profile.problems_chat_id

    # Шаг 5: Отправляем POST запрос с нужными данными
    url = f"http://{TG_FLASK_ADDRESS}/api/send_problem"
    data = {
        "id": application_id,
        "username": username,
        "problem": problem,
        "problems_chat_id": problems_chat_id  # Добавляем поле problems_chat_id
    }

    response = requests.post(url, json=data)

    # Логируем результат
    if response.status_code == 200:
        # Предполагаем, что API возвращает JSON-ответ, который можно проверить
        response_data = response.json()
        if response_data.get("status") == "success":
            return True, None
        else:
            # Возвращаем ошибки, если статус не "success"
            errors = response_data.get("errors", [])
            return False, f"Ошибка при отправке данных: {errors}"
    else:
        # Если запрос не успешен, возвращаем статус код и текст ответа
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
