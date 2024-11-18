from django.utils.dateformat import format
from database.models import Application, WithdrawalRequest


def get_completed_applications(user, end_date=None):
    filter_params = {
        'executor': user.id,
        'status': 'completed',
    }

    # Если передана дата окончания, добавляем фильтр по completed_time
    if end_date:
        filter_params['completed_time__lte'] = end_date

    applications = Application.objects.filter(**filter_params)
    return applications


def get_withdrawal_requests(user, end_date=None):
    # Базовые параметры фильтрации: по пользователю и статусу
    filter_params = {
        'user': user,
    }

    # Если дата окончания передана, добавляем фильтр по execution_date
    if end_date:
        filter_params['execution_date__lte'] = end_date

    # Получаем отфильтрованные запросы с сортировкой по id
    withdrawals = WithdrawalRequest.objects.filter(**filter_params).order_by('-id')
    return withdrawals


def get_withdrawal_requests_data(withdrawals_page):
    return [
        {
            'id': withdrawal.id,
            'user': withdrawal.user.username,  # Имя пользователя, если нужно
            'amount': f"{withdrawal.amount:.2f}",  # Форматируем с двумя знаками после запятой
            'status': withdrawal.status,
            'status_display': withdrawal.get_status_display(),  # Отображение статуса
            'request_date': withdrawal.request_date,
            'execution_date': withdrawal.execution_date,
            'transaction_hash': withdrawal.transaction_hash,
        }
        for withdrawal in withdrawals_page
    ]
