import os

from dotenv import load_dotenv

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from main_site.utils.generate_fiilename_and_valid_file import generate_unique_filename, is_valid_file_type
from main_site.utils.get_banks import get_bank_name_by_index
from main_site.utils.telegram_api import send_application_data

load_dotenv()
SITE_URL = os.getenv('SITE_URL')


@csrf_protect
def upload_receipt(request):
    if request.method == 'POST':
        try:
            # Получаем ID заявки
            application_id = request.POST.get('application_id')
            application = get_object_or_404(Application, id=application_id, user_id=request.user.id)

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
                return JsonResponse({"error": "Недопустимый формат файла. Разрешены только PDF и изображения (JPEG, "
                                              "PNG)."}, status=400)

            # Сохраняем файл с уникальным именем
            unique_filename = generate_unique_filename(receipt_file.name)
            fs = FileSystemStorage()
            filename = fs.save(f"receipts/{unique_filename}", receipt_file)
            file_url = fs.url(filename)

            # Обновляем данные заявки
            application.has_receipt = True
            application.receipt_link = file_url
            application.from_bank = bank_name
            application.status = 'processing'
            application.save()

            # Отправляем данные через send_application_data
            result, error = send_application_data(application_id)

            if error:
                return JsonResponse({"error": error}, status=400)

            # Возвращаем успешный ответ с ссылкой на файл
            return JsonResponse({
                "status": "success",
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Неподдерживаемый метод"}, status=405)


