from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.timezone import now
from decimal import Decimal
import os
import json
from django.conf import settings

from database.models.application import Application
from database.models.user_profile import UserProfile
from django.contrib.auth.models import User
from finApplications.globals import active_timers
from main_site.services.telegram_notification import telegram_balance_warning


def confirm_application(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')

        # Находим заявку по ID
        application = get_object_or_404(Application, id=application_id)

        # Проверяем, что заявка имеет статус 'processing'
        if application.status == 'processing':
            # Получаем пользователя заявки
            user = get_object_or_404(User, id=application.executor.id)
            user_profile = get_object_or_404(UserProfile, user=user)
            percentage = user_profile.percentage

            # Получаем merchant_id и профиль мерчанта
            merchant_profile = get_object_or_404(UserProfile, user_id=application.merchant)
            merchant_percentage = merchant_profile.merchant_percentage

            # Загружаем среднюю цену из файла
            file_path = os.path.join(settings.BASE_DIR, 'finApplications', 'average_price.json')
            with open(file_path, 'r') as file:
                data = json.load(file)
            average_price = Decimal(data['average_price'])

            # Рассчитываем net_amount_in_usdt для пользователя
            adjusted_usdt_user = average_price - (average_price * (percentage / 100))
            net_amount_in_usdt = application.amount / adjusted_usdt_user

            # Проверка, что рассчитанная сумма положительная
            if net_amount_in_usdt <= 0:
                return JsonResponse({'status': 'error', 'error': 'Неверная сумма после расчета'}, status=400)

            # Обновляем заработок пользователя
            user_profile.earnings += net_amount_in_usdt
            user_profile.save()

            # Рассчитываем сумму списания для мерчанта
            adjusted_usdt_merchant = average_price - (average_price * (merchant_percentage / 100))
            merchant_deduction = application.amount / adjusted_usdt_merchant

            # Проверка, что сумма списания положительная
            if merchant_deduction <= 0:
                return JsonResponse({'status': 'error', 'error': 'Неверная сумма для списания с мерчанта'}, status=400)

            # Списываем с баланса мерчанта
            merchant_profile.merchant_balance -= merchant_deduction
            # if merchant_profile.merchant_balance <= 500:
            #     telegram_balance_warning(merchant_profile.user.username)
            # elif merchant_profile.merchant_balance < 0:
            #     telegram_balance_warning(merchant_profile.user.username, True)
            merchant_profile.save()

            # Удаляем активный таймер, если он есть
            if application_id in active_timers:
                del active_timers[application_id]

            # Обновляем заявку
            application.status = 'completed'
            application.net_amount_in_usdt = net_amount_in_usdt
            application.completed_time = now()
            application.closing_rate = average_price
            application.rate_after_fee = adjusted_usdt_user
            application.merchant_rate_after_fee = adjusted_usdt_merchant
            application.percentage = percentage
            application.save()

            return JsonResponse({'status': 'success'})

        else:
            return JsonResponse({'status': 'error', 'error': 'Неверный статус заявки'}, status=400)

    return JsonResponse({'status': 'error', 'error': 'Неверный запрос'}, status=400)
