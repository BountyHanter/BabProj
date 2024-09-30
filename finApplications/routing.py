from django.urls import path

from finApplications import consumers

websocket_urlpatterns = [
    path('ws/update/', consumers.DatabaseUpdateConsumer.as_asgi()),
]