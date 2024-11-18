from datetime import datetime
import pytz


def filter_applications(request, applications):
    # Фильтрация по статусу заявки
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    # Фильтрация по диапазону дат
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Устанавливаем московскую временную зону
    timezone = pytz.timezone("Europe/Moscow")

    # Преобразуем 'date_from' и 'date_to' в объекты datetime с временной зоной МСК
    if date_from:
        date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone)
        applications = applications.filter(created_at__gte=date_from_parsed)

    if date_to:
        date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").replace(tzinfo=timezone)
        applications = applications.filter(created_at__lte=date_to_parsed)

    return applications


def get_applications_data(applications_page):
    return [
        {
            'id': app.id,
            'type': app.type,
            'amount': f"{app.amount:.2f}",  # Форматируем с двумя знаками после запятой
            'payment_details': app.payment_details,
            'to_bank': app.to_bank,
            'from_bank': app.from_bank,  # Оставляем None, если поле пустое
            'status': app.status,
            'status_display': app.get_status_display(),  # Отображение статуса
            'created_at': app.created_at,
            'taken_time': app.taken_time,
            'completed_time': app.completed_time,
            'receipt_link': app.receipt_link,
        }
        for app in applications_page
    ]