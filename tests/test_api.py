# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import overpass
import geojson
import pickle
import os


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


def test_geojson_extended():

    class API(overpass.API):
        def _get_from_overpass(self, query):
            return pickle.load(open(os.path.join(os.path.dirname(__file__), "example.response"), "rb"))

    # api = overpass.API()
    # osm_geo = api.get("rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);", verbosity='body geom')
    # pickle.dump(api._get_from_overpass("[out:json];rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);out body geom;"),
    #             open(os.path.join(os.path.dirname(__file__), "example.response"), "wb"),
    #             protocol=2)
    # geojson.dump(osm_geo, open(os.path.join(os.path.dirname(__file__), "example.json"), "w"))

    api = API()
    osm_geo = api.get("rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);", verbosity='body geom')
    ref_geo = geojson.load(open(os.path.join(os.path.dirname(__file__), "example.json"), "r"))
    assert osm_geo==ref_geo
