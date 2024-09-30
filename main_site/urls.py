from django.urls import path
from django.http import HttpResponseRedirect


from main_site.services.confirm_application_logic import confirm_application
from main_site.services.take_application_logic import take_application
from main_site.utils.save_receipt_file import upload_receipt
from main_site.utils.send_problem_data import report_problem
from main_site.utils.send_request_withdrawal import request_withdrawal
from main_site.views import get_application_info, user_applications_view, personal_cabinet, trigger_error


def redirect_to_applications(request):
    return HttpResponseRedirect('/user-applications/')


urlpatterns = [
    path('', redirect_to_applications),  # Перенаправление с корневого URL на /statistics/

    path('take_application/', take_application, name='take_application'),
    path('upload-receipt/', upload_receipt, name='upload_receipt'),
    path('confirm-application/', confirm_application, name='confirm_application'),

    path('get_application_info/', get_application_info, name='get_application_info'),

    path('user-applications/', user_applications_view, name='user_applications'),

    path('report_problem/', report_problem, name='report_problem'),

    # path('api/process/', process_result, name='process_result'),

    path('personal_cabinet/', personal_cabinet, name='personal_cabinet'),
    path('request_withdrawal/', request_withdrawal, name='request_withdrawal'),
    path('trigger-error/', trigger_error),

]


