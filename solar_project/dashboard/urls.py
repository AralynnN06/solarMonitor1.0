from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_with_pivot, name='dashboard_with_pivot'),
    path('dashboard/data', views.pivot_data, name='pivot_data'),
    path("api/esp/ingest/", views.esp_ingest, name="esp_ingest"),
    path("api/esp/latest/", views.esp_latest, name="esp_latest"),
    path("api/esp/sensors/", views.esp_sensors, name="esp_sensors"),
    path("api/esp/series/", views.esp_series, name="esp_series"),
    path("api/esp/net_power_daily/", views.esp_net_power_daily, name="esp_net_power_daily"),
    path("api/esp/net_energy_daily/", views.esp_net_energy_daily, name="esp_net_energy_daily"),
    path("api/utility/rate/", views.utility_rate, name="utility_rate"),
    path("api/utility/states/", views.utility_states, name="utility_states"),
    path("api/utility/custom/", views.utility_custom, name="utility_custom"),

]
