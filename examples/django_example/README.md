# Django example application

This is a barebones Django application that uses `overpass-api-python-wrapper` to display OSM data on a Leaflet map.

The key components are
* The [view](https://github.com/mvexel/overpass-api-python-wrapper/blob/example/examples/django_example/leafletapp/views.py#L9) that gets the OSM data from Overpass;
* The [Javascript function](https://github.com/mvexel/overpass-api-python-wrapper/blob/example/examples/django_example/leafletapp/static/leafletapp/overpass.js#L19) that asynchronouysly calls this endpoint.

If you want to try it for yourself:
* `cd` to the `examples/django_example` directory (where this README lives)
* `pip install -r requirements`
* `./manage.py runserver`
* Point your browser at `http://localhost:8000/`