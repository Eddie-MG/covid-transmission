from django.urls import path

from . import views

app_name = 'intro'

urlpatterns = [
    path('', views.home, name='home'),
    path('disclaimer', views.disclaimber, name='disc'),
]
