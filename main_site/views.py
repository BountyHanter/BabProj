from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse

from django.utils import timezone

from database.models import Application, WithdrawalRequest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from dotenv import load_dotenv

from finApplications.ByBit import take_bybit_price

import json
import os
from django.conf import settings  # Для работы с путями к статическим файлам

load_dotenv()
SITE_URL = os.getenv('SITE_URL')
DOMAIN = os.getenv('DOMAIN')


@csrf_protect
@login_required
def user_applications_view(request):
    user = request.user
    profile = user.profile

    user_id = request.user.id

    # Найдем активную заявку с учетом статусов 'active', 'processing', 'approved'
    active_application = (
        Application.objects.filter(user_id=user_id, status__in=['active', 'processing', 'approved'])
        .first()
    )
    # Заявки, которые не являются 'new', 'active', 'processing' или 'approved'
    other_applications = Application.objects.filter(user_id=user_id).exclude(
        status__in=['new', 'active', 'processing', 'approved']
    )

    # Сортировка
    order_by = request.GET.get('order_by', 'id')  # Изменено на 'id'
    direction = request.GET.get('direction', 'desc')  # Изменено на 'desc'

    if direction == 'desc':
        order_by = f'-{order_by}'

    other_applications = other_applications.order_by(order_by)

    # Путь к файлу banks.json
    banks_json_path = os.path.join(settings.BASE_DIR, 'main_site', 'banks.json')

    bybit_data = take_bybit_price()
    # Получение текущего курса и времени замера курса из профиля пользователя
    current_course = bybit_data['average_price']
    course_taken_at = bybit_data['time']

    balance = profile.earnings

    try:
        # Чтение файла banks.json
        with open(banks_json_path, 'r', encoding='utf-8') as f:
            banks_json = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Обработка ошибок при чтении файла
        banks_json = []
        # Логирование ошибки (можно использовать logging)
        print(f"Ошибка при чтении banks.json: {e}")

    # Дополнительно: если есть активная заявка, передаем ее банк
    bank_name = None
    if active_application:
        bank_name = active_application.bank_name

    context = {
        'active_application': active_application,
        'other_applications': other_applications,
        'current_order_by': order_by.strip('-'),
        'current_direction': direction,
        'banks_json': json.dumps(banks_json),
        'bank_name': bank_name,
        'site_url': SITE_URL,
        'active_page': "user_applications",
        'current_course': current_course,
        'course_taken_at': course_taken_at,
        'balance': balance,
        'DOMAIN': DOMAIN,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main_site/user_app_template.html', context)

    return render(request, 'main_site/user_applications.html', context)


@login_required
def get_application_info(request):
    application_id = request.GET.get('application_id')
    application = get_object_or_404(Application, id=application_id, user_id=request.user.id)

    data = {
        'status': application.status,
        'type': application.type,
        'amount': application.amount,
        'payment_details': application.payment_details,
        'bank_name': application.bank_name,
        'receipt_link': f"{SITE_URL}{application.receipt_link}" if application.receipt_link else None,
    }
    return JsonResponse(data)


@login_required
def personal_cabinet(request):
    user = request.user
    profile = user.profile

    bybit_data = take_bybit_price()
    # Получение текущего курса и времени замера курса из профиля пользователя
    current_course = bybit_data['average_price']
    course_taken_at = bybit_data['time']

    balance = profile.earnings

    is_active = profile.active

    _now = timezone.now()
    start_of_today = _now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - timedelta(days=_now.weekday())  # Начало недели (понедельник)
    start_of_month = _now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Статистика по заявкам
    applications = Application.objects.filter(user_id=user.id)

    applications_stats = {
        'today_count': applications.filter(created_at__gte=start_of_today).count(),
        'today_sum': applications.filter(created_at__gte=start_of_today).aggregate(Sum('amount'))['amount__sum'] or 0,
        'week_count': applications.filter(created_at__gte=start_of_week).count(),
        'week_sum': applications.filter(created_at__gte=start_of_week).aggregate(Sum('amount'))['amount__sum'] or 0,
        'month_count': applications.filter(created_at__gte=start_of_month).count(),
        'month_sum': applications.filter(created_at__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0,
        'all_time_count': applications.count(),
        'all_time_sum': applications.aggregate(Sum('amount'))['amount__sum'] or 0,
    }

    # Статистика по запросам на вывод средств
    withdrawals = WithdrawalRequest.objects.filter(user=user)

    withdrawals_stats = {
        'today_count': withdrawals.filter(request_date__gte=start_of_today).count(),
        'today_sum': withdrawals.filter(request_date__gte=start_of_today).aggregate(Sum('amount'))['amount__sum'] or 0,
        'week_count': withdrawals.filter(request_date__gte=start_of_week).count(),
        'week_sum': withdrawals.filter(request_date__gte=start_of_week).aggregate(Sum('amount'))['amount__sum'] or 0,
        'month_count': withdrawals.filter(request_date__gte=start_of_month).count(),
        'month_sum': withdrawals.filter(request_date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0,
        'all_time_count': withdrawals.count(),
        'all_time_sum': withdrawals.aggregate(Sum('amount'))['amount__sum'] or 0,
    }

    # Список запросов на вывод средств пользователя
    withdrawal_requests = withdrawals.order_by('-request_date')

    context = {
        'current_course': current_course,
        'course_taken_at': course_taken_at,
        'is_active': is_active,
        'applications_stats': applications_stats,
        'withdrawals_stats': withdrawals_stats,
        'withdrawal_requests': withdrawal_requests,
        'balance': balance,
        'DOMAIN': DOMAIN,
    }

    return render(request, 'main_site/personal_cabinet.html', context)

def custom_404(request, exception):
    try:
        with open('/var/www/babdata.cloud/html/404.html', 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), status=404)
    except Exception as e:
        # В случае ошибки чтения файла, вернуть простой ответ
        return HttpResponse("Страница не найдена", status=404)

def custom_500(request):
    try:
        with open('/var/www/babdata.cloud/html/500.html', 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), status=500)
    except Exception as e:
        # В случае ошибки чтения файла, вернуть простой ответ
        return HttpResponse("Внутренняя ошибка сервера", status=500)


# @csrf_exempt  # Отключаем проверку CSRF для POST-запросов
# def process_result(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             item_id = data.get("id")
#             result = data.get("result")
#
#             # Проверяем, что result содержит корректное значение (1 или 2)
#             if result not in ["0", "1"]:
#                 return JsonResponse({"status": "error", "message": "Invalid result value"}, status=400)
#
#             # Ищем заявку по item_id
#             application = get_object_or_404(Application, id=item_id)
#
#             # Устанавливаем статус в зависимости от значения result
#             if result == "0":
#                 application.status = 'approved'
#                 send_update_to_user(application.user_id, application.id)
#                 print('Одобрена')
#                 application.completed_time = timezone.now()  # Устанавливаем текущее время
#
#             elif result == "1":
#                 application.status = 'canceled'
#                 send_update_to_user(application.user_id, application.id, action='cancel')
#                 print('ОТМЕНЕНА')
#                 application.completed_time = timezone.now()  # Устанавливаем текущее время
#
#             # Сохраняем изменения
#             application.save()
#
#             # Возвращаем JSON-ответ
#             return JsonResponse({"status": "success", "id": item_id, "new_status": application.status}, status=200)
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"Error: {str(e)}"}, status=400)
#     return JsonResponse({"status": "error", "message": "Only POST requests allowed"}, status=405)

from django.http import HttpResponse

def trigger_error(request):
    # Искусственно вызываем ошибку
    division_by_zero = 1 / 0
    return HttpResponse("This won't be reached.")
