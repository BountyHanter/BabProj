from datetime import timedelta

import requests
from dotenv import load_dotenv
import json
import os

from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from database.models.withdrawals import WithdrawalRequest
from finApplications import settings
from finApplications.ByBit import take_bybit_price
from report_service.excel_report_func import generate_excel_report

from main_site.utils.banks_name import get_bank_names

load_dotenv()
SITE_URL = os.getenv('SITE_URL')
DOMAIN = os.getenv('DOMAIN')


@csrf_protect
@login_required
def user_applications_view(request):
    user = request.user
    profile = user.profile

    user_id = request.user.id

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

    bybit_data = take_bybit_price()
    # Получение текущего курса и времени замера курса из профиля пользователя
    current_course = bybit_data['average_price']

    balance = profile.earnings

    context = {
        'other_applications': other_applications,
        'current_order_by': order_by.strip('-'),
        'current_direction': direction,
        'current_course': current_course,
        'balance': balance,
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main_site/user_app_template.html', context)

    return render(request, 'main_site/user_applications.html', context)


@csrf_protect
@login_required
def active_application_view(request):
    user_id = request.user.id

    # Получение активной заявки с определенными статусами
    active_application = Application.objects.filter(
        user_id=user_id,
        status__in=['active', 'processing', 'approved']
    ).first()

    bybit_data = take_bybit_price()  # Предполагается, что эта функция определена
    current_course = bybit_data['average_price']
    course_taken_at = bybit_data['time']
    balance = request.user.profile.earnings  # Предполагается, что у пользователя есть профиль с балансом

    context = {
        'active_application': active_application,
        'banks_json': json.dumps(get_bank_names()),
        'current_course': current_course,
        'course_taken_at': course_taken_at,
        'balance': balance,
        'websocket_url': DOMAIN
    }

    # Проверка на AJAX-запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main_site/partials/active_application_partial.html', context)

    return render(request, 'main_site/active_application.html', context)


@login_required
def get_application_info(request):
    application_id = request.GET.get('application_id')
    application = get_object_or_404(Application, id=application_id, user_id=request.user.id)

    data = {
        'status': application.status,
        'type': application.type,
        'amount': application.amount,
        'payment_details': application.payment_details,
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


@csrf_protect
@login_required
def generate_report(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Получаем данные из запроса
        data = json.loads(request.body.decode('utf-8'))

        # Печатаем данные в консоль для отладки
        result_link = generate_excel_report(request, data)
        # Возвращаем ответ об успешной обработке
        return JsonResponse({'file_url': result_link}, status=200)
    else:
        can_view_all_reports = request.user.is_superuser or request.user.has_perm('main_site.can_view_all_reports')
        context = {
            'banks_json': json.dumps(get_bank_names()),
            'can_view_all_reports': can_view_all_reports,

        }
        return render(request, 'main_site/generate_report.html', context)


@login_required
def protected_media(request, path):
    # Путь к локальному файлу
    media_path = os.path.join(settings.MEDIA_ROOT, path)

    # Проверяем, есть ли файл на локальном сервере
    if os.path.exists(media_path):
        return FileResponse(open(media_path, 'rb'))

    # Если файл отсутствует на локальном сервере, запрашиваем его на удалённом
    media_url = f'http://147.45.245.11/media/{path}'
    response = requests.get(media_url)

    if response.status_code == 200:
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    else:
        raise Http404("Файл не найден.")


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


