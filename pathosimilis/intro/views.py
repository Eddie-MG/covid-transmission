from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect


# Create your views here.

def home(request):
    return render(request, 'intro/home.html')


def disclaimber(request):
    return render(request, 'intro/disclaimer.html')
