from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from database.models.application import Application
from finApplications.ByBit_utils import get_bybit_price
from main_site.utils.merchant_dashboards_utils import filter_applications, get_applications_data, \
    get_ajax_applications_data
from main_site.utils.paginate_utils import paginate_with_range
from main_site.utils.total_amount import calculate_total_amount


@login_required
def merchant_dashboard(request):
    # Получаем и фильтруем заявки
    applications_by_id = Application.objects.filter(merchant=request.user).order_by('-id')
    applications = filter_applications(request, applications_by_id)

    # Параметры пагинации из GET-запроса
    rows_per_page = int(request.GET.get('rows_per_page', 15) or 15)
    page_number = int(request.GET.get('page', 1) or 1)

    # Используем функцию для пагинации и получения диапазона страниц
    applications_page, page_range, total_pages = paginate_with_range(applications, page_number, rows_per_page)
    #
    # # Данные заявок
    # applications_data = get_applications_data(applications_page)
    # print(applications_data)
    print(get_ajax_applications_data(applications_page))


    # Контекст для шаблона
    context = {
        'total_amount': calculate_total_amount(),
        'bybit_price': get_bybit_price(),
        'merchant_balance': request.user.profile.merchant_balance,
        'applications': applications_page,
        'total_pages': total_pages,
        'current_page': page_number,
        'rows_per_page': rows_per_page,
        'page_range': page_range,  # Передаем диапазон страниц в шаблон
    }

    # Проверка на AJAX-запрос
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'applications': get_ajax_applications_data(applications_page),
            'total_pages': total_pages,
            'current_page': page_number,
            'rows_per_page': rows_per_page,
        })
    else:
        return render(request, 'main_site/statistics.html', context)
