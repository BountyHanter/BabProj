from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from finApplications.ByBit_utils import get_bybit_price
from finApplications.globals import SITE_URL, WEBSOCKET_URL
from main_site.utils.banks_name import get_bank_names
from main_site.utils.paginate_utils import paginate_with_range
from main_site.utils.user_applications_utils import search_other_applications, get_other_applications_data



@csrf_protect
@login_required
def user_applications_view(request):
    user = request.user
    profile = user.profile
    username = request.user.username
    balance = profile.earnings
    is_active = profile.active

    search_text = request.GET.get('search', None)

    other_applications = search_other_applications(user, search_text)

    # Параметры пагинации из GET-запроса
    rows_per_page = int(request.GET.get('rows_per_page', 15) or 15)
    page_number = int(request.GET.get('page', 1) or 1)

    # Используем функцию для пагинации и получения диапазона страниц
    other_applications_page, page_range, total_pages = paginate_with_range(other_applications, page_number, rows_per_page)

    # Данные заявок
    other_applications_data = get_other_applications_data(other_applications_page)

    context = {
        'bybit_price': get_bybit_price(),
        'username': username,
        'is_active': is_active,
        'balance': balance,
        'other_applications': other_applications_data,
        'page_range': page_range,
        'total_pages': total_pages,
        'page_number': page_number,  # Текущая страница
        'rows_per_page': rows_per_page,  # Количество строк на странице

    }

    return render(request, 'main_site/user_applications.html', context)


@csrf_protect
@login_required
def active_application_view(request):
    user = request.user
    profile = user.profile
    username = request.user.username

    is_active = profile.active
    user_id = user.id

    # Получение активной заявки с определенными статусами
    active_application = Application.objects.filter(
        executor=user_id,
        status__in=['active', 'processing']
    ).first()

    balance = request.user.profile.earnings  # Предполагается, что у пользователя есть профиль с балансом
    context = {
        'bybit_price': get_bybit_price(),
        'is_active': is_active,
        'username': username,
        'active_application': active_application,
        'banks': get_bank_names(),
        'balance': balance,
        'websocket_url': WEBSOCKET_URL
    }

    # Проверка на AJAX-запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'main_site/partials/active_application_main_header.html', context)

    return render(request, 'main_site/active_application.html', context)


# @login_required
# def get_application_info(request):
#     application_id = request.GET.get('application_id')
#     application = get_object_or_404(Application, id=application_id, executor=request.user.id)
#
#     data = {
#         'status': application.status,
#         'type': application.type,
#         'amount': application.amount,
#         'payment_details': application.payment_details,
#         'receipt_link': f"{SITE_URL}{application.receipt_link}" if application.receipt_link else None,
#     }
#     return JsonResponse(data)
