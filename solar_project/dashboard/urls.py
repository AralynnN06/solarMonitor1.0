from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard_with_pivot, name='dashboard_with_pivot'),
    path('data', views.pivot_data, name='pivot_data'),
    path("api/esp/ingest/", views.esp_ingest, name="esp_ingest"),
    path("api/esp/latest/", views.esp_latest, name="esp_latest"),

]