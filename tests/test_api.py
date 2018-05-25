# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import overpass


def test_initialize_api():
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False


def test_geojson():
    api = overpass.API(debug=True)

    map_query = overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635)
    osm_geo = api.get(map_query)
    assert len(osm_geo["features"]) > 1

    osm_geo = api.get("node(area:3602758138)[amenity=cafe]")
    assert len(osm_geo["features"]) > 1
