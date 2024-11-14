import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse, Http404

from finApplications import settings


@login_required
def protected_media(request, path):
    # Путь к локальному файлу
    media_path = os.path.join(settings.MEDIA_ROOT, path)

    # Проверяем, есть ли файл на локальном сервере
    if os.path.exists(media_path):
        return FileResponse(open(media_path, 'rb'))

    # Если файл отсутствует на локальном сервере, запрашиваем его на удалённом
    media_url = f'https://media.babdata.cloud/media/{path}'
    response = requests.get(media_url)

    if response.status_code == 200:
        return HttpResponse(response.content, content_type=response.headers['Content-Type'])
    else:
        raise Http404("Файл не найден.")
