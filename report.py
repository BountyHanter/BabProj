import os
import django
from django.contrib.auth.models import User

from report_service.excel_report_func import generate_excel_report

# Параметры
user = User.objects.get(username='2')
request = type('Request', (object,), {'user': user})()
filter_data = {
    'status': 'active',

}
type_user = 'Merchant'

# Запуск функции
result = generate_excel_report(request, filter_data, type_user)
print(result)
