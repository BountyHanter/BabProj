from django.db.models import Sum

from database.models import Application


def calculate_total_amount():
    # Фильтруем записи по статусам и суммируем поле `amount`
    total_amount = Application.objects.filter(status__in=['new', 'active', 'processing']).aggregate(Sum('amount'))[
        'amount__sum']

    # Если в выборке не было записей, сумма будет None, поэтому заменяем на 0
    return total_amount if total_amount is not None else 0
