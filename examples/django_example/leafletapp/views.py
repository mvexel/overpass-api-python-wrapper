from django.shortcuts import render

def home(request):
    return render(request, 'leafletapp/index.html', None)
