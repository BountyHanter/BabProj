from threading import Timer

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.timezone import now
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from database.models import Application, UserProfile
from finApplications.globals import active_timers
from main_site.tasks import cancel_application


@csrf_protect
@login_required
@transaction.atomic
def take_application(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Этот метод поддерживает только POST-запросы"}, status=405)

    user = request.user  # Получаем текущего пользователя

    try:
        user_profile = user.profile  # Предполагается, что UserProfile всегда создается
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "Профиль пользователя не найден."}, status=400)

    # Проверяем, активен ли пользователь для обработки заявок
    if not user_profile.active:
        return JsonResponse(
            {"error": "Вы не можете брать заявки, так как ваша возможность обработки заявок отключена."}, status=403)

    user_id = user.id  # Получаем ID пользователя

    # Проверка на наличие активной заявки
    active_application = Application.objects.select_for_update().filter(user_id=user_id, status='active').first()
    if active_application:
        return JsonResponse({"error": "У вас уже есть активная заявка"}, status=400)

    # Формируем условия для фильтрации заявок по сумме
    min_amount = user_profile.min_amount
    max_amount = user_profile.max_amount

    # Если указаны оба значения, фильтруем по диапазону
    if min_amount > 0 and max_amount > 0:
        amount_filter = Q(amount__gte=min_amount) & Q(amount__lte=max_amount)
    # Если указан только минимальный порог
    elif min_amount > 0:
        amount_filter = Q(amount__gte=min_amount)
    # Если указан только максимальный порог
    elif max_amount > 0:
        amount_filter = Q(amount__lte=max_amount)
    else:
        # Если оба значения равны 0, не добавляем фильтрацию по сумме
        amount_filter = Q()

    # Попытка взять новую заявку, соответствующую сумме
    application = Application.objects.select_for_update().filter(status='new').filter(amount_filter).order_by('id').first()

    if application:
        # Обновляем заявку
        application.user_id = user_id
        application.taken_time = now()
        application.status = 'active'
        application.save()

        # Таймер для автоматической отмены заявки через 30 минут (30 * 60 секунд)
        timer = Timer(30 * 60, cancel_application, [application.id])
        timer.start()
        active_timers[application.id] = timer

        # Возвращаем статус успеха
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error": "Нет новых заявок"}, status=404)
