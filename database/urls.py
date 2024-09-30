from django.urls import path

from database.views.api_views import ApplicationCreateView, ApplicationUpdateView, BanksListAPIView, \
    ApplicationStatusView


urlpatterns = [
    # API
    path('applications/create/', ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/edit/', ApplicationUpdateView.as_view(), name='application-edit'),
    path('application/status/', ApplicationStatusView.as_view(), name='application_status'),
    path('banks/', BanksListAPIView.as_view(), name='banks_list_api'),


]

