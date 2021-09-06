# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import overpass
import geojson
import pickle
import pytest

from tests import load_resource


PARAM_GEOJSON = ((overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635), 'map_query_response.json'),
                 ('node(area:3602758138)[amenity=cafe]', 'map_query_response.json'))


PARAM_ERRORS = ((400, overpass.errors.OverpassSyntaxError, '[out:json];Alpha;out body;'),
                (429, overpass.errors.MultipleRequestsError, ''),
                (504, overpass.errors.ServerLoadError, '25'))


def test_initialize_api(requests):
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False
    assert not requests.get.called
    assert not requests.post.called


@pytest.mark.parametrize('query, response_file', PARAM_GEOJSON)
def test_geojson(requests, query, response_file):
    requests.response._content = load_resource(response_file)
    api = overpass.API(debug=True)
    osm_geo = api.get(query)
    assert osm_geo["features"]
    assert requests.post.called
    assert requests.post.call_args.args == ('https://overpass-api.de/api/interpreter',)
    assert not requests.get.called


def test_geojson_extended(requests):

    class API(overpass.API):
        def _get_from_overpass(self, query):
            return pickle.loads(load_resource('example.response'))
    api = API()
    osm_geo = api.get("rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);", verbosity='body geom')
    ref_geo = geojson.loads(load_resource('example.json'))
    assert osm_geo == ref_geo
    assert not requests.get.called
    assert not requests.post.called


@pytest.mark.parametrize('status_code, class_error, error_str', PARAM_ERRORS)
def test_api_errors(status_code, class_error, error_str, requests):
    requests.response.status_code = status_code

    with pytest.raises(class_error) as error:
        overpass.API().get('Alpha')
    assert str(error.value) == error_str
