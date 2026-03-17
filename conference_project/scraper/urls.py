from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("records/", views.records, name="records"),

    path("export/csv/", views.export_csv, name="export_csv"),

    path("export/excel/", views.export_excel, name="export_excel"),
]