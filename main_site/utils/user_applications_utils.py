from django.db.models import Q

from database.models import Application


def search_other_applications(user, search_text=None):
    # Фильтрация по полю executor
    applications = Application.objects.filter(
        executor=user
    ).exclude(
        status__in=['new', 'active', 'processing']
    ).order_by('-id')

    # Если текст не передан, возвращаем все заявки пользователя
    if not search_text:
        return applications

    # Создание Q-объекта для поиска совпадений по всем указанным полям
    query = Q(id__icontains=search_text) | \
            Q(to_bank__icontains=search_text)

    # Применение фильтрации по созданному запросу
    result = applications.filter(query)

    return result


def get_other_applications_data(applications_page):
    return [
        {
            'id': application.id,
            'type': application.get_type_display(),  # Отображение типа
            'amount': f"{application.amount:.2f}",  # Форматируем с двумя знаками после запятой
            'payment_details': application.payment_details,
            'to_bank': application.to_bank,
            'from_bank': application.from_bank,
            'status': application.status,
            'created_at': application.created_at,
            'taken_time': application.taken_time,
            'completed_time': application.completed_time,
            'receipt_link': application.receipt_link
        }
        for application in applications_page
    ]
