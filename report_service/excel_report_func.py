import os
import json
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
banks_path = os.path.join(BASE_DIR, 'main_site/banks.json')

# Чтение банков из файла
with open(banks_path, 'r', encoding='utf-8') as file:
    banks_data = json.load(file)['dictionary']
bank_mapping = {str(index + 1): bank['bankName'] for index, bank in enumerate(banks_data)}


@shared_task
def generate_excel_report(request, filter_data):
    # Создание нового Excel файла
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчёт"

    # Определяем, есть ли у пользователя право просматривать все отчёты или он в группе 'Merchant'
    can_view_all = request.user.has_perm('report.can_view_all_reports')
    is_merchant = request.user.groups.filter(name='Merchants').exists()

    # Формируем заголовки в зависимости от прав
    headers = ['ID заявки']
    if can_view_all:
        headers.append('Дата создания')
    headers.extend(['Дата исполнения', 'Тип заявки', 'Реквизиты', 'User', 'Сумма', 'Валюта',
                    'Статус', 'Банк получателя', 'Банк исполнителя', 'Курс на момент исполнения',
                    'Курс после вычета комиссии', 'Комиссия в %', 'Сумма в USDT', 'Ссылка на чек'])
    ws.append(headers)

    # Фильтрация заявок
    applications = Application.objects.all()

    # Если пользователь имеет право на просмотр всех отчётов
    if can_view_all:
        # Применяются только фильтры, не касающиеся пользователей (например, по заявкам, банкам и т.д.)
        pass  # Уже применены другие фильтры выше (по датам, банкам и т.д.)

    # Если пользователь в группе "Merchants"
    elif is_merchant:
        # Скрытая фильтрация по его merchant_id
        applications = applications.filter(merchant_id=request.user.id)

    # Если пользователь не имеет прав и не состоит в группе "Merchants"
    else:
        # Скрытая фильтрация по его user_id
        applications = applications.filter(user_id=request.user.id)

    # Применяем фильтры по id заявок
    if filter_data.get('application_id_from'):
        applications = applications.filter(id__gte=filter_data['application_id_from'])
    if filter_data.get('application_id_to'):
        applications = applications.filter(id__lte=filter_data['application_id_to'])

    # Применяем фильтры по типу
    if filter_data.get('type'):
        applications = applications.filter(type=filter_data['type'])

    # Применяем фильтры по статусу
    if filter_data.get('status'):
        applications = applications.filter(status__in=filter_data['status'])

    # Фильтруем по банкам
    if filter_data.get('from_bank'):
        bank_names = [bank_mapping.get(bank_id) for bank_id in filter_data['from_bank']]
        applications = applications.filter(from_bank__in=bank_names)
    if filter_data.get('to_bank'):
        bank_names = [bank_mapping.get(bank_id) for bank_id in filter_data['to_bank']]
        applications = applications.filter(to_bank__in=bank_names)

    # Фильтрация по суммам
    if filter_data.get('amount_from'):
        applications = applications.filter(amount__gte=filter_data['amount_from'])
    if filter_data.get('amount_to'):
        applications = applications.filter(amount__lte=filter_data['amount_to'])

    # Фильтрация по датам создания и завершения
    if filter_data.get('creation_date_from'):
        applications = applications.filter(created_at__gte=filter_data['creation_date_from'])
    if filter_data.get('creation_date_to'):
        applications = applications.filter(created_at__lte=filter_data['creation_date_to'])
    if filter_data.get('completion_date_from'):
        applications = applications.filter(completed_time__gte=filter_data['completion_date_from'])
    if filter_data.get('completion_date_to'):
        applications = applications.filter(completed_time__lte=filter_data['completion_date_to'])

    for app in applications:
        user_name = app._user.username if app._user else 'N/A'
        row = [app.id]
        if can_view_all:
            created_at = app.created_at.strftime('%Y-%m-%d %H:%M') if app.created_at else 'N/A'
            row.append(created_at)
        completed_time = app.completed_time.strftime('%Y-%m-%d %H:%M') if app.completed_time else 'N/A'
        row.extend([
            completed_time,
            app.type,
            app.payment_details,
            user_name,
            app.amount,
            'RUB',  # Валюта всегда RUB
            app.status,
            app.to_bank,
            app.from_bank,
            app.closing_rate,
            app.rate_after_fee,
            app.percentage,
            app.net_amount_in_usdt,
            f'{SITE_URL}{app.receipt_link}',
        ])
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


