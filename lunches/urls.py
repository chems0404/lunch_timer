from django.urls import path
from . import views

urlpatterns = [
    path("", views.kiosk_home, name="kiosk_home"),
    path("colaborador/<int:collaborator_id>/", views.collaborator_status, name="collaborator_status"),
    path("colaborador/<int:collaborator_id>/iniciar/", views.start_lunch, name="start_lunch"),
    path("colaborador/<int:collaborator_id>/finalizar/", views.end_lunch, name="end_lunch"),

    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/exportar-csv/", views.export_lunches_csv, name="export_lunches_csv"),
]