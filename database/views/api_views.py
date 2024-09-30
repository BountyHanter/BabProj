import json
import os

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database.models import Application
from database.serializers import ApplicationSerializer
from database.utils.authenticate_client import authenticate_client


class ApplicationCreateView(APIView):
    """
    API view который позволяет создать новую заявку.
    """
    def post(self, request):
        # Аутентификация через Client-Id и Api-Key
        error_response, api_key_obj = authenticate_client(request)
        if error_response:
            return error_response

        # Обрабатываем данные заявки
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            # Добавляем merchant_id из найденного APIKey
            application = serializer.save(merchant_id=api_key_obj.user.id)
            return Response({
                "status": "created",
                "id": application.id
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "description": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ApplicationUpdateView(APIView):
    """
    API view, который позволяет отредактировать заявку.
    """
    def put(self, request, pk):
        # Аутентификация через Client-Id и Api-Key
        error_response, api_key_obj = authenticate_client(request)
        if error_response:
            return error_response

        # Попытка найти заявку по ID
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "description": "Заявка не найдена."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка принадлежности заявки мерчанту
        if application.merchant_id != api_key_obj.user.id:
            return Response(
                {
                    "status": "error",
                    "description": "Вы не можете редактировать эту заявку, так как её создал другой мерчант."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем статус заявки
        if application.status != "new":
            return Response(
                {
                    "status": "error",
                    "description": "Заявка уже в работе и не может быть отредактирована."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем наличие данных для обновления
        if not request.data:
            return Response(
                {
                    "status": "error",
                    "description": "Не переданы данные для обновления."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Валидируем и сохраняем изменения
        serializer = ApplicationSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "updated",
                    "id": application.id
                },
                status=status.HTTP_200_OK
            )

        # Возвращаем ошибки валидации
        return Response(
            {
                "status": "error",
                "description": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class BanksListAPIView(APIView):
    """
    API view для возврата списка банков из файла banks.json
    """
    def get(self, request, *args, **kwargs):
        # Аутентификация через Client-Id и Api-Key
        error_response, api_key_obj = authenticate_client(request)
        if error_response:
            return error_response

        # Путь к файлу banks.json
        file_path = os.path.join(settings.BASE_DIR, 'database', 'banks.json')

        # Чтение файла и загрузка данных
        with open(file_path, 'r', encoding='utf-8') as f:
            banks_data = json.load(f)

        # Возвращаем данные в виде JSON ответа через API
        return Response(banks_data)


class ApplicationStatusView(APIView):
    """
    API view для получения статуса заявки по ID или Customer.
    """

    def get(self, request):
        # Аутентификация через Client-Id и Api-Key
        error_response, api_key_obj = authenticate_client(request)
        if error_response:
            return error_response

        # Получаем id и customer из параметров запроса
        application_id = request.query_params.get('id')

        # Проверяем, что хотя бы один из параметров передан
        if not application_id:
            return Response({
                "status": "error",
                "description": "Необходимо передать 'id'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Если передан 'id', проверяем, что это целое число
        if application_id:
            try:
                application_id = int(application_id)
            except ValueError:
                return Response({
                    "status": "error",
                    "description": "'id' должен быть integer."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Ищем заявку по id
            try:
                application = Application.objects.get(id=application_id)
            except Application.DoesNotExist:
                return Response({
                    "status": "error",
                    "description": "Заявки с данным ID не существует."
                }, status=status.HTTP_404_NOT_FOUND)

        # Возвращаем статус заявки
        return Response({
            "status": "success",
            "application_status": application.status,
            "application_id": application.id,
        }, status=status.HTTP_200_OK)
