from dotenv import load_dotenv
import requests

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from main_site.utils.generate_fiilename_and_valid_file import generate_unique_filename, is_valid_file_type
from main_site.utils.get_banks import get_bank_name_by_index
from main_site.utils.telegram_api import send_application_data

load_dotenv()
MEDIA_SERVER_URL = 'https://media.babdata.cloud/upload/'  # URL для загрузки файла на удалённый сервер


@csrf_protect
def upload_receipt(request):
    if request.method == 'POST':
        try:
            # Получаем ID заявки
            application_id = request.POST.get('application_id')
            application = get_object_or_404(Application, id=application_id, executor=request.user
                                            )

            # Проверяем статус заявки
            if application.status != 'active':
                return JsonResponse({"error": "Нельзя изменить данные заявки так как её статус изменён"}, status=400)

            # Получаем ID банка и проверяем его существование
            bank_id = request.POST.get('bank_id')
            bank_name = get_bank_name_by_index(bank_id)
            if not bank_name:
                return JsonResponse({"error": "Банк с данным ID не найден"}, status=400)

            # Проверяем наличие файла
            if 'receipt' not in request.FILES:
                return JsonResponse({"error": "Файл чека не найден"}, status=400)

            # Получаем файл чека
            receipt_file = request.FILES['receipt']

            # Проверяем тип файла (должен быть PDF или изображение)
            if not is_valid_file_type(receipt_file):
                return JsonResponse({"error": "Недопустимый формат файла. Разрешены только PDF и изображения (JPEG, PNG)."}, status=400)

            # Генерируем уникальное имя файла
            unique_filename = generate_unique_filename(receipt_file.name)

            # Отправляем файл на удалённый сервер
            files = {
                'receipt': (unique_filename, receipt_file.read(), receipt_file.content_type)
            }
            response = requests.post(MEDIA_SERVER_URL, files=files)

            if response.status_code != 200:
                return JsonResponse({"error": "Ошибка загрузки файла на удалённый сервер"}, status=500)

            # Получаем URL загруженного файла и сохраняем только относительный путь
            file_url = response.json().get('file_url')
            relative_file_url = file_url.replace('http://147.45.245.11', '')
            

            # Обновляем данные заявки
            application.has_receipt = True
            application.receipt_link = relative_file_url  # Сохраняем относительный путь
            application.from_bank = bank_name
            application.status = 'processing'
            application.save()

            # Отправляем данные через send_application_data
            result, error = send_application_data(application_id)

            if error:
                return JsonResponse({"error": error}, status=400)

            # Возвращаем успешный ответ
            return JsonResponse({
                "status": "success",
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Неподдерживаемый метод"}, status=405)


