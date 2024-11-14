from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group

from database.models.api_keys import APIKey


def authenticate_client(request):
    """
    Проверка Client-Id и Api-Key.
    Возвращает объект APIKey, если аутентификация успешна и пользователь принадлежит к группе Merchants,
    или Response с ошибкой.
    """
    client_id = request.headers.get('Client-Id')
    api_key_plain = request.headers.get('Api-Key')


    # Проверяем наличие Client-Id и Api-Key
    if not client_id or not api_key_plain:
        return Response({
            "status": "error",
            "description": "Требуется Client_Id и Api_Key."
        }, status=status.HTTP_400_BAD_REQUEST), None

    # Ищем запись APIKey по client_id
    try:
        api_key_obj = APIKey.objects.get(client_id=client_id)
    except APIKey.DoesNotExist:
        return Response({
            "status": "error",
            "description": "Неверный Client ID."
        }, status=status.HTTP_400_BAD_REQUEST), None

    # Проверяем Api-Key
    if not check_password(api_key_plain, api_key_obj.api_key):
        return Response({
            "status": "error",
            "description": "Неверный Api Key."
        }, status=status.HTTP_403_FORBIDDEN), None

    # Проверка на принадлежность к группе 'Merchants'
    merchant_group = Group.objects.get(name='Merchants')
    if not api_key_obj.user.groups.filter(id=merchant_group.id).exists():
        return Response({
            "status": "error",
            "description": "У пользователя нет доступа к API."
        }, status=status.HTTP_403_FORBIDDEN), None

    # Если всё хорошо, возвращаем None для ошибки и объект api_key_obj
    return None, api_key_obj
