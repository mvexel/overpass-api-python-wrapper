from django.shortcuts import render
from django.http import JsonResponse
import json
import overpass

def home(request):
    return render(request, 'leafletapp/index.html', None)

def get_from_overpass(request, osmtype, key, value, min_lon, min_lat, max_lon, max_lat):
	overpass_query = '{type}[{key}={value}]({min_lat}, {min_lon}, {max_lat}, {max_lon})'.format(
		type=osmtype,
		key=key,
		value=value,
		min_lon=min_lon,
		min_lat=min_lat,
		max_lon=max_lon,
		max_lat=max_lat)
	api = overpass.API()
	response = api.Get(overpass_query)
	return JsonResponse(response)