from django.urls import path
from django.http import HttpResponseRedirect

from database.views.media import protected_media
from main_site.services.confirm_application_logic import confirm_application
from main_site.services.take_application_logic import take_application
from main_site.test_csrf import test_csrf
from main_site.utils.save_receipt_file import upload_receipt
from main_site.utils.send_problem_data import report_problem
from main_site.utils.send_request_withdrawal import request_withdrawal
from main_site.views.personal_cabinet import personal_cabinet
from main_site.views.reports import user_generate_report, merchant_generate_report
from main_site.views.user_applications import active_application_view, get_application_info, user_applications_view


def redirect_to_applications(request):
    return HttpResponseRedirect('/user_applications/')


urlpatterns = [
    path('', redirect_to_applications),  # Перенаправление с корневого URL на /statistics/

    path('active_application/', active_application_view, name="active_application"),

    path('take_application/', take_application, name='take_application'),
    path('upload_receipt/', upload_receipt, name='upload_receipt'),
    path('confirm-application/', confirm_application, name='confirm_application'),

    path('get_application_info/', get_application_info, name='get_application_info'),

    path('user_applications/', user_applications_view, name='user_applications'),

    path('report_problem/', report_problem, name='report_problem'),

    # path('api/process/', process_result, name='process_result'),

    path('personal_cabinet/', personal_cabinet, name='personal_cabinet'),
    path('request_withdrawal/', request_withdrawal, name='request_withdrawal'),

    path('user_generate_report/', user_generate_report, name='user_generate_report'),

    path('media/<path:path>/', protected_media, name='protected_media'),

    path('merchant_generate_report/', merchant_generate_report, name='m_generate_report'),
    path('test-csrf/', test_csrf, name='test_csrf'),

]


