from django.urls import path, re_path
from dashboard.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('chat/', views.chat, name='chat'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
