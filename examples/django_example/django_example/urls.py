from django.conf.urls import url, patterns
from leafletapp import views

urlpatterns = [
    url(r'^$', views.home, name='home')
]
