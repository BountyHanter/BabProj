from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from database.models.application import Application


@login_required
def merchant_dashboard(request):
    # Получаем текущего пользователя
    current_user = request.user

    # Получаем заявки, связанные с этим мерчантом
    applications = Application.objects.filter(merchant_id=current_user.id)

    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    # Фильтрация по дате создания
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        applications = applications.filter(created_at__gte=start_date)
    if end_date:
        applications = applications.filter(created_at__lte=end_date)

    # Сортировка
    order_by = request.GET.get('order_by', 'id')  # По умолчанию сортировка по ID
    direction = request.GET.get('direction', 'asc')

    # Применение сортировки в зависимости от направления
    if direction == 'desc':
        order_by = f'-{order_by}'

    applications = applications.order_by(order_by)

    total_created = applications.total_created()
    total_completed = applications.total_completed()
    total_amount = applications.total_amount()

    context = {
        'applications': applications,
        'current_order_by': order_by.strip('-'),
        'current_direction': direction,
        'total_created': total_created,
        'total_completed': total_completed,
        'total_amount': total_amount,
    }
    return render(request, 'database/statistics.html', context)
