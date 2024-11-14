import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect

from finApplications.ByBit_utils import get_bybit_price
from main_site.utils.banks_name import get_bank_names
from main_site.utils.total_amount import calculate_total_amount
from report_service.excel_report_func import generate_excel_report


@csrf_protect
@login_required
def user_generate_report(request):
    user = request.user
    profile = user.profile
    user_name = request.user.username

    is_active = profile.active

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Получаем данные из запроса
        data = json.loads(request.body.decode('utf-8'))

        # Печатаем данные в консоль для отладки
        result_link = generate_excel_report(request, data, "User")
        # Возвращаем ответ об успешной обработке
        return JsonResponse({'file_url': result_link}, status=200)
    else:
        context = {
            'bybit_price': get_bybit_price(),
            'balance': request.user.profile.earnings,
            'banks': get_bank_names(),
            'is_active': is_active,
            'user_name': user_name,
        }
        return render(request, 'main_site/u_generate_report.html', context)


@csrf_protect
@login_required
def merchant_generate_report(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Получаем данные из запроса
        data = json.loads(request.body.decode('utf-8'))
        # Печатаем данные в консоль для отладки
        result_link = generate_excel_report(request, data, "Merchant")
        # Возвращаем ответ об успешной обработке
        return JsonResponse({'file_url': result_link}, status=200)
    else:
        context = {
            'total_amount': calculate_total_amount(),
            'bybit_price': get_bybit_price(),
            'balance': request.user.profile.earnings,
            'banks': get_bank_names(),

        }
        return render(request, 'main_site/m_generate_report.html', context)
