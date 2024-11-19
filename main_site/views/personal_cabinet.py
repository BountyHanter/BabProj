from datetime import datetime
import pytz

from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from finApplications.ByBit_utils import get_bybit_price, get_bybit_time
from finApplications.globals import DOMAIN
from main_site.utils.paginate_utils import paginate_with_range
from main_site.utils.personal_cabinet_utils import get_completed_applications, get_withdrawal_requests, \
    get_withdrawal_requests_data

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

@login_required
def personal_cabinet(request):
    user = request.user
    profile = user.profile
    username = request.user.username
    balance = profile.earnings
    is_active = profile.active

    date_filter_withdrawal = request.GET.get('date_withdrawal', None)
    date_filter_application = request.GET.get('date_application', None)

    # Преобразуем `date_withdrawal` и `date_application` в `timezone-aware` формат с московским временем
    if date_filter_withdrawal:
        date_filter_withdrawal = MOSCOW_TZ.localize(datetime.strptime(date_filter_withdrawal, "%Y-%m-%d"))
    if date_filter_application:
        date_filter_application = MOSCOW_TZ.localize(datetime.strptime(date_filter_application, "%Y-%m-%d"))

    withdrawals = get_withdrawal_requests(user, date_filter_withdrawal)

    # Параметры пагинации из GET-запроса
    rows_per_page = int(request.GET.get('rows_per_page', 15) or 15)
    page_number = int(request.GET.get('page', 1) or 1)

    # Используем функцию для пагинации и получения диапазона страниц
    withdrawal_page, page_range, total_pages = paginate_with_range(withdrawals, page_number, rows_per_page)

    # Данные заявок
    withdrawals_data = get_withdrawal_requests_data(withdrawal_page)

    # Статистика по заявкам
    applications = get_completed_applications(user, date_filter_application)

    context = {
        'bybit_price': get_bybit_price(),
        'bybit_time': get_bybit_time(),
        'username': username,
        'is_active': is_active,
        'balance': balance,
        'applications_count': applications.count(),
        'withdrawals': withdrawals_data,
        'page_range': page_range,
        'total_pages': total_pages,
        'page_number': page_number,  # Текущая страница
        'rows_per_page': rows_per_page,  # Количество строк на странице
        'all_time_sum': applications.aggregate(Sum('amount'))['amount__sum'] or 0,
        'DOMAIN': DOMAIN,
    }

    return render(request, 'main_site/personal_cabinet.html', context)
