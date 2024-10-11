from django.contrib.auth.models import User
from django.contrib import admin

from database.admin_custom.applications_admin import ApplicationAdmin
from database.admin_custom.excel_report_admin import ReportAdmin
from database.admin_custom.logs_admin import AdminActionLogAdmin
from database.admin_custom.custom_user_admin import CustomUserAdmin
from database.admin_custom.withdrawals_admin import WithdrawalRequestAdmin
from database.models.application import Application
from database.models.excel_reports import Report
from database.models.logs import AdminActionLog
from database.models.withdrawals import WithdrawalRequest

# Переопределяем стандартное действие удаления глобально, чтобы не удаляли без логирования
admin.site.disable_action('delete_selected')

# Регистрация админских классов
admin.site.register(Application, ApplicationAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(AdminActionLog, AdminActionLogAdmin)
admin.site.register(Report, ReportAdmin)

# Перерегистрируем модель пользователя с обновленной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

