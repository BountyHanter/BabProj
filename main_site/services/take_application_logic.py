from threading import Timer

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.timezone import now
from django.db.models import Q, Subquery, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from database.models.user_profile import UserProfile
from finApplications.globals import active_timers
from main_site.tasks import cancel_application


@csrf_protect
@login_required
@transaction.atomic
def take_application(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Этот метод поддерживает только POST-запросы"}, status=405)

    user = request.user

    try:
        user_profile = user.profile
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "Профиль пользователя не найден."}, status=400)

    if not user_profile.active:
        return JsonResponse(
            {"error": "Вы не можете брать заявки, так как ваша возможность обработки заявок отключена."},
            status=403)

    user_id = user.id

    # Проверяем, есть ли у пользователя активная заявка
    active_application_exists = Application.objects.filter(
        executor=user_id, status='active'
    ).exists()
    if active_application_exists:
        return JsonResponse({"error": "У вас уже есть активная заявка"}, status=400)

    # Формируем фильтры для заявок
    filters = Q(status='new')

    if user_profile.recipients_bank:
        filters &= Q(to_bank__in=user_profile.recipients_bank)

    if user_profile.min_amount and user_profile.max_amount:
        filters &= Q(amount__gte=user_profile.min_amount, amount__lte=user_profile.max_amount)
    elif user_profile.min_amount:
        filters &= Q(amount__gte=user_profile.min_amount)
    elif user_profile.max_amount:
        filters &= Q(amount__lte=user_profile.max_amount)

    # Идентификаторы мерчантов с балансом ниже лимита
    merchants_below_limit = UserProfile.objects.filter(
        merchant_balance__lt=F('merchant_limit')
    ).values_list('user_id', flat=True)

    filters &= ~Q(merchant_id__in=merchants_below_limit)

    # Пытаемся взять новую заявку
    application = Application.objects.select_for_update().filter(filters).order_by('id').first()

    if application:
        application.executor = request.user
        application.taken_time = now()
        application.status = 'active'
        application.save()

        timer = Timer(30 * 60, cancel_application, [application.id])
        timer.start()
        active_timers[application.id] = timer

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"error": "Нет новых заявок"}, status=404)
