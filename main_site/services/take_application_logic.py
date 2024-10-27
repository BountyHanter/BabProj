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
            {"error": "Вы не можете брать заявки, так как ваша возможность обработки заявок отключена."}, status=403)

    user_id = user.id

    active_application = Application.objects.select_for_update().filter(executor=user_id, status='active').first()
    if active_application:
        return JsonResponse({"error": "У вас уже есть активная заявка"}, status=400)

    min_amount = user_profile.min_amount
    max_amount = user_profile.max_amount

    if min_amount > 0 and max_amount > 0:
        amount_filter = Q(amount__gte=min_amount) & Q(amount__lte=max_amount)
    elif min_amount > 0:
        amount_filter = Q(amount__gte=min_amount)
    elif max_amount > 0:
        amount_filter = Q(amount__lte=max_amount)
    else:
        amount_filter = Q()

    # Находим ID мерчантов с балансом ниже лимита
    merchants_below_limit = UserProfile.objects.filter(
        merchant_balance__lt=F('merchant_limit')
    ).values('user')

    # Ищем подходящую заявку, исключая заявки от мерчантов с низким балансом
    application = (Application.objects
                   .select_for_update()
                   .filter(status='new')
                   .filter(amount_filter)
                   .exclude(merchant_id__in=Subquery(merchants_below_limit))
                   .order_by('id')
                   .first())

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
