from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from database.models.application import Application
from main_site.utils.telegram_api import send_problem_data


@csrf_protect
@transaction.atomic
def report_problem(request):
    if request.method == 'POST':
        try:
            # Получаем ID заявки и описание проблемы из данных формы
            application_id = request.POST.get('application_id')
            problem = request.POST.get('problem')

            print(request.POST)

            # Проверяем, указана ли проблема
            if not problem:
                return JsonResponse({"error": "Описание проблемы обязательно"}, status=400)

            # Находим заявку
            application = get_object_or_404(Application, id=int(application_id), executor=request.user)

            # Меняем статус заявки на 'manual' и записываем проблему
            application.status = 'manual'
            application.problem = problem
            print(f"Перед сохранением: status={application.status}, problem={application.problem}")
            application.save()
            print("Сохранение завершено")
            print(application.status)

            # # # Отправляем данные через send_application_data
            # result, error = send_problem_data(application_id)
            # if error:
            #     return JsonResponse({"error": error}, status=400)

            # Возвращаем успешный ответ
            return JsonResponse({
                "status": "success",
                "message": "Заявка обновлена и проблема зафиксирована"
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Неподдерживаемый метод"}, status=405)
