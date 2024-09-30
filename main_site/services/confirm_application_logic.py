from decimal import Decimal

from django.contrib.auth.models import User


from database.models import Application, UserProfile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import json
import os
from django.conf import settings  # Для работы с путями к статическим файлам


def confirm_application(request):
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        # Находим заявку по ID
        application = get_object_or_404(Application, id=application_id)

        # Проверяем, что заявка имеет статус 'processing'
        if application.status == 'processing':
            # Получаем пользователя по user_id  из заявки
            user = get_object_or_404(User, id=application.user_id)

            # Получаем профиль пользователя
            user_profile = get_object_or_404(UserProfile, user=user)

            # Получаем процент пользователя
            percentage = user_profile.percentage

            file_path = os.path.join(settings.BASE_DIR, 'finApplications', 'average_price.json')

            with open(file_path, 'r') as file:
                data = json.load(file)

            average_price = Decimal(data['average_price'])

            # Рассчитываем net_amount_in_usdt
            adjusted_usdt = average_price - (average_price * (percentage / 100))
            net_amount_in_usdt = application.amount / adjusted_usdt

            # Проверяем рассчитанную сумму
            if net_amount_in_usdt <= 0:
                return JsonResponse({'status': 'error', 'error': 'Неверная сумма после расчета'}, status=400)

            # Обновляем earnings
            user_profile.earnings = Decimal(user_profile.earnings) + net_amount_in_usdt
            user_profile.save()

            # Обновляем заявку
            application.status = 'completed'
            application.net_amount_in_usdt = net_amount_in_usdt
            application.save()

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'error': 'Неверный статус заявки'}, status=400)

    return JsonResponse({'status': 'error', 'error': 'Неверный запрос'}, status=400)
