import os
import json
from datetime import datetime

import pytz
from celery import shared_task
from pathlib import Path
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from dotenv import load_dotenv
from openpyxl import Workbook
from io import BytesIO
from database.models import Application
from database.models.excel_reports import Report

load_dotenv()
SITE_URL = os.getenv('SITE_URL')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
banks_path = os.path.join(BASE_DIR, 'main_site/../database/banks.json')

# Чтение банков из файла
with open(banks_path, 'r', encoding='utf-8') as file:
    banks_data = json.load(file)['dictionary']
bank_mapping = {str(index + 1): bank['bankName'] for index, bank in enumerate(banks_data)}


@shared_task
def generate_excel_report(request, filter_data, type_user):
    # Создание нового Excel файла
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчёт"

    # Заголовки столбцов
    headers = ['ID заявки', 'Дата создания', 'Дата исполнения', 'Тип заявки', 'Реквизиты', 'Исполнитель', 'Сумма', 'Валюта',
               'Статус', 'Банк получателя', 'Банк отправителя', 'Курс на момент исполнения',
               'Курс после вычета комиссии', 'Комиссия в %', 'Сумма в USDT', 'Ссылка на чек']
    ws.append(headers)

    # Получение всех заявок
    applications = Application.objects.all()

    # Фильтрация по типу пользователя
    if type_user == 'User':
        applications = applications.filter(executor=request.user)
    elif type_user == 'Merchant':
        applications = applications.filter(merchant=request.user)

    print(request.user)

    # Функция для преобразования строки в дату
    def parse_date(date_str):
        try:
            # Преобразуем строку в объект datetime
            naive_date = datetime.strptime(date_str, '%Y-%m-%d')
            # Преобразуем в осознанное время с временной зоной Москвы
            return pytz.timezone('Europe/Moscow').localize(naive_date)
        except (ValueError, TypeError):
            return None

    # Фильтрация по дате создания заявки
    if filter_data.get('date_created_from'):
        date_created_from = parse_date(filter_data['date_created_from'])
        if date_created_from:
            applications = applications.filter(created_at__gte=date_created_from)
    if filter_data.get('date_created_to'):
        date_created_to = parse_date(filter_data['date_created_to'])
        if date_created_to:
            applications = applications.filter(created_at__lte=date_created_to)

    # Фильтрация по дате выполнения заявки
    if filter_data.get('date_completed_from'):
        date_completed_from = parse_date(filter_data['date_completed_from'])
        if date_completed_from:
            applications = applications.filter(completed_time__gte=date_completed_from)
    if filter_data.get('date_completed_to'):
        date_completed_to = parse_date(filter_data['date_completed_to'])
        if date_completed_to:
            applications = applications.filter(completed_time__lte=date_completed_to)

    # Фильтрация по типу транзакции
    if filter_data.get('transaction_type'):
        applications = applications.filter(type=filter_data['transaction_type'])

    # Фильтрация по статусу
    if filter_data.get('status'):
        applications = applications.filter(status=filter_data['status'])

    # Фильтрация по банку отправителя
    if filter_data.get('bank_sender'):
        applications = applications.filter(from_bank=filter_data['bank_sender'])

    # Фильтрация по банку получателя
    if filter_data.get('bank_receiver'):
        applications = applications.filter(to_bank=filter_data['bank_receiver'])

    # Фильтрация по суммам
    if filter_data.get('amount_from'):
        try:
            amount_from = float(filter_data['amount_from'])
            applications = applications.filter(amount__gte=amount_from)
        except ValueError:
            pass  # Если значение некорректно, пропускаем фильтр
    if filter_data.get('amount_to'):
        try:
            amount_to = float(filter_data['amount_to'])
            applications = applications.filter(amount__lte=amount_to)
        except ValueError:
            pass

    for app in applications:
        user_name = app.executor.username if app.executor else 'N/A'
        created_at = app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else 'N/A'
        completed_time = app.completed_time.strftime('%Y-%m-%d %H:%M') if app.completed_time else 'N/A'
        row = [
            app.id,
            created_at,
            completed_time,
            app.type,
            app.payment_details,
            user_name,
            app.amount,
            'RUB',  # Валюта
            app.status,
            app.to_bank,
            app.from_bank,
            app.closing_rate,
            app.rate_after_fee,
            app.percentage,
            app.net_amount_in_usdt,
            f'{SITE_URL}{app.receipt_link}',
        ]
        ws.append(row)

    # Сохраняем файл в памяти
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Путь для сохранения файла на сервере
    report_name = f"report_{timezone.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    report_path = os.path.join(settings.MEDIA_ROOT, 'reports', report_name)

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    wb.save(report_path)

    report_link = f'/media/reports/{report_name}'

    report = Report.objects.create(
        user=request.user,
        report_link=report_link,
        application_count=applications.count()
    )

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={report_name}'

    return f'{SITE_URL}{report_link}'


