import json
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from database.models.withdrawals import WithdrawalRequest
from main_site.utils.telegram_api import send_request_withdrawal


@login_required
def request_withdrawal(request):
    if request.method == 'POST':
        username = request.user.username
        # Извлечение данных из JSON-запроса
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
        except (json.JSONDecodeError, KeyError, TypeError):
            return JsonResponse({'success': False, 'message': 'Неверный формат данных.'}, status=400)

        # Проверка и конвертация суммы
        try:
            amount = Decimal(amount)
            if amount <= 0:
                return JsonResponse({'success': False, 'message': 'Сумма должна быть положительной.'}, status=400)
        except (InvalidOperation, TypeError):
            return JsonResponse({'success': False, 'message': 'Неверная сумма.'}, status=400)

        profile = request.user.profile
        available_amount = profile.earnings

        # Проверка достаточности средств
        if profile.earnings < amount:
            return JsonResponse({'success': False, 'message': 'Недостаточно средств.'}, status=400)

        # Создание запроса на вывод средств
        WithdrawalRequest.objects.create(
            user=request.user,
            amount=amount,
            status='processing',
        )

        # Обновление заработка пользователя
        profile.earnings -= amount
        profile.save()

        result, error = send_request_withdrawal(float(amount), float(available_amount), username)
        if error:
            return JsonResponse({"error": error}, status=400)

        return JsonResponse({'success': True, 'message': 'Запрос на вывод средств успешно создан.'})
    else:
        return JsonResponse({'success': False, 'message': 'Неверный тип запроса.'}, status=405)
