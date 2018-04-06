#!/usr/bin/env python

import overpass

api = overpass.API()
response = api.get('node["name"="Salt Lake City"]')
print(response)
print [(
    feature['properties']['name'],
    feature['id']) for feature in response["features"]]
