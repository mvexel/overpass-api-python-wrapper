from django.conf.urls import url, patterns
from leafletapp import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^overpass/'
    	'(?P<osmtype>node|way)/'
    	'(?P<key>[a-z]+)/'
    	'(?P<value>[a-z\-]+)/'
    	'(?P<min_lat>\d+\.\d+)/'
    	'(?P<min_lon>-?\d+\.\d+)/'
    	'(?P<max_lat>\d+\.\d+)/' 
    	'(?P<max_lon>-?\d+\.\d+)$',
    	views.get_from_overpass,
    	name='overpass'),
]
