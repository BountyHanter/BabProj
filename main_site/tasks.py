from database.models.application import Application
from finApplications.globals import active_timers


def cancel_application(application_id):
    try:
        application = Application.objects.get(id=application_id)
        if application.status == 'active':
            application.status = 'canceled'
            application.save()
            # Удаляем таймер из словаря после отмены
            if application_id in active_timers:
                del active_timers[application_id]
    except Application.DoesNotExist:
        pass
