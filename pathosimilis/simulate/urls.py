from django.urls import path

from . import views
from .views import App

app_name = 'sim'
a = App()
urlpatterns = [
    path('', a.sumilate, name='sumilate'),
    path('results', a.results, name='res'),
]
