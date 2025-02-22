from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
import requests

from finApplications.globals import MEDIA_SERVER_URL


@login_required
def protected_media(request, path):
    # Запрашиваем файл на удалённом сервере
    media_url = f'{MEDIA_SERVER_URL}{path}'
    response = requests.get(media_url, stream=True)  # stream=True для больших файлов

    if response.status_code == 200:
        # Возвращаем файл напрямую из ответа удалённого сервера
        return HttpResponse(response.raw, content_type=response.headers.get('Content-Type', 'application/octet-stream'))
    else:
        # Если файл не найден на удалённом сервере
        raise Http404("Файл не найден.")
