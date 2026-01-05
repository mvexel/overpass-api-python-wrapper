# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Union

import geojson

import pytest
from deepdiff import DeepDiff
from shapely.geometry import shape
from shapely.geometry import mapping as shapely_mapping

import overpass
from overpass.models import GeoJSONFeatureCollection
from overpass.utils import Utils
from overpass.errors import (
    MultipleRequestsError,
    OverpassSyntaxError,
    ServerLoadError,
    UnknownOverpassError,
)

USE_LIVE_API = os.getenv("USE_LIVE_API", "").lower() == "true"


def test_initialize_api():
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False


@pytest.mark.parametrize(
    "query,length,response",
    [
        (
            overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635),
            1,
            Path("tests/example_mapquery.json"),
        ),
        (
            "node(area:3602758138)[amenity=cafe]",
            1,
            Path("tests/example_singlenode.json"),
        ),
    ],
)
def test_geojson(
    query: Union[overpass.MapQuery, str], length: int, response: Path, requests_mock
):
    api = overpass.API(debug=True)

    with response.open() as fp:
        mock_response = json.load(fp)
    requests_mock.post("//overpass-api.de/api/interpreter", json=mock_response)

    osm_geo = api.get(query)
    assert len(osm_geo["features"]) > length

    osm_model = api.get(query, model=True)
    assert osm_model.features


def test_json_response(requests_mock):
    api = overpass.API()
    mock_response = {"elements": [{"id": 1, "type": "node"}]}
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        json=mock_response,
        headers={"content-type": "application/json"},
    )
    response = api.get("node(1)", responseformat="json")
    assert response == mock_response

    model_response = api.get("node(1)", responseformat="json", model=True)
    assert model_response.elements[0].id == 1
    assert model_response.elements[0].type == "node"


def test_csv_response(requests_mock):
    api = overpass.API()
    csv_body = "name\t@lon\t@lat\nSpringfield\t-3.0\t56.2\n"
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        text=csv_body,
        headers={"content-type": "text/csv"},
    )
    response = api.get(
        'node["name"="Springfield"]["place"]', responseformat="csv(name,::lon,::lat)"
    )
    assert response == [["name", "@lon", "@lat"], ["Springfield", "-3.0", "56.2"]]

    model_response = api.get(
        'node["name"="Springfield"]["place"]', responseformat="csv(name,::lon,::lat)", model=True
    )
    assert model_response.header == ["name", "@lon", "@lat"]
    assert model_response.rows == [["Springfield", "-3.0", "56.2"]]


def test_xml_response(requests_mock):
    api = overpass.API()
    xml_body = "<osm><node id=\"1\" lat=\"0\" lon=\"0\" /></osm>"
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        text=xml_body,
        headers={"content-type": "application/osm3s+xml"},
    )
    response = api.get("node(1)", responseformat="xml")
    assert response == xml_body

    model_response = api.get("node(1)", responseformat="xml", model=True)
    assert model_response.text == xml_body


@pytest.mark.integration
def test_multipolygon():
    """
    Test that multipolygons are processed without error
    """
    if not os.getenv("RUN_NETWORK_TESTS"):
        pytest.skip("requires live Overpass API; set RUN_NETWORK_TESTS=1")
    api = overpass.API()
    api.get("rel(11038555)", verbosity="body geom")


@pytest.mark.parametrize(
    "verbosity,response,output",
    [
        ("body geom", "tests/example_body.json", "tests/example_body.geojson"),
        # ("tags geom", "tests/example.json", "tests/example.geojson"),
        ("meta geom", "tests/example_meta.json", "tests/example_meta.geojson"),
    ],
)
def test_geojson_extended(verbosity, response, output, requests_mock):
    api = overpass.API(debug=True)

    with Path(response).open() as fp:
        mock_response = json.load(fp)
    requests_mock.post("//overpass-api.de/api/interpreter", json=mock_response)

    osm_geo = sorted(
        api.get(
            f"rel(6518385);out {verbosity};way(10322303);out {verbosity};node(4927326183);",
            verbosity=verbosity,
        )
    )

    with Path(output).open() as fp:
        ref_geo = sorted(geojson.load(fp))
    assert osm_geo == ref_geo


def test_geo_interface_roundtrip():
    with Path("tests/example_body.geojson").open() as fp:
        raw_geojson = json.load(fp)

    model = GeoJSONFeatureCollection.model_validate(raw_geojson)
    first_geom = model.features[0].geometry
    assert first_geom is not None

    model_shape = shape(first_geom.__geo_interface__)
    raw_shape = shape(raw_geojson["features"][0]["geometry"])
    assert shapely_mapping(model_shape) == shapely_mapping(raw_shape)


def test_invalid_overpass_response_raises(requests_mock):
    api = overpass.API()
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        json={"foo": "bar"},
        headers={"content-type": "application/json"},
    )
    with pytest.raises(UnknownOverpassError):
        api.get("node(1)")


def test_invalid_json_response_raises(requests_mock):
    api = overpass.API()
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        text="<html>not json</html>",
        headers={"content-type": "application/json"},
    )
    with pytest.raises(UnknownOverpassError):
        api.get("node(1)", responseformat="json")


def test_invalid_overpass_response_build_false(requests_mock):
    api = overpass.API()
    response = {"foo": "bar"}
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        json=response,
        headers={"content-type": "application/json"},
    )
    assert api.get("node(1)", build=False) == response


# You can also comment the pytest decorator to run the test against the live API
@pytest.mark.skipif(
    not USE_LIVE_API, reason="USE_LIVE_API environment variable not set to True"
)
def test_geojson_live():
    """
    This code should only be executed once when major changes to the Overpass API and/or to this
    wrapper are introduced. One than has to manually verify that the date in the example.geojson
    file from the Overpass API matches the data in the example.geojson file generated by this
    wrapper.

    The reason for this approach is the following: It is not safe to make calls to the actual API in
    this test as the API might momentarily be unavailable and the underlying data can also change
    at any moment.
    """
    api = overpass.API(debug=True)
    osm_geo = api.get(
        "rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);",
        verbosity="body geom",
    )

    with Path("tests/example_live.json").open("r") as fp:
        ref_geo = json.load(fp)

    # assert that the dictionaries are the same
    # diff = DeepDiff(osm_geo, ref_geo, include_paths="[root]['features']")
    diff = DeepDiff(osm_geo, ref_geo, include_paths="[root]['features']")
    print(diff if diff else "No differences found")

    assert not diff


@pytest.mark.parametrize(
    "response,slots_available,slots_running,slots_waiting",
    [
        (Path("tests/overpass_status/no_slots_waiting_six_lines.txt"), 2, (), ()),
        (Path("tests/overpass_status/no_slots_waiting.txt"), 2, (), ()),
        (
            Path("tests/overpass_status/one_slot_running.txt"),
            1,
            (
                datetime(
                    year=2021,
                    month=3,
                    day=8,
                    hour=20,
                    minute=22,
                    second=55,
                    tzinfo=timezone.utc,
                ),
            ),
            (),
        ),
        (
            Path("tests/overpass_status/one_slot_waiting.txt"),
            1,
            (),
            (
                datetime(
                    year=2021,
                    month=3,
                    day=8,
                    hour=20,
                    minute=23,
                    second=28,
                    tzinfo=timezone.utc,
                ),
            ),
        ),
        (
            Path("tests/overpass_status/two_slots_waiting.txt"),
            0,
            (),
            (
                datetime(
                    year=2021,
                    month=3,
                    day=8,
                    hour=20,
                    minute=27,
                    second=00,
                    tzinfo=timezone.utc,
                ),
                datetime(
                    year=2021,
                    month=3,
                    day=8,
                    hour=20,
                    minute=30,
                    second=28,
                    tzinfo=timezone.utc,
                ),
            ),
        ),
    ],
)
def test_api_status(
    response: Path,
    slots_available: int,
    slots_running: Tuple[datetime],
    slots_waiting: Tuple[datetime],
    requests_mock,
):
    mock_response = response.read_text()
    requests_mock.get("https://overpass-api.de/api/status", text=mock_response)

    api = overpass.API(debug=True)

    requests_mock.post("https://overpass-api.de/api/interpreter", json={"elements": []})
    map_query = overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635)
    api.get(map_query)

    assert 0 <= api.slots_available <= 2
    assert api.slots_available == slots_available

    assert isinstance(api.slots_running, tuple)
    assert api.slots_running == slots_running

    assert isinstance(api.slots_waiting, tuple)
    assert api.slots_waiting == slots_waiting

    assert isinstance(api.slot_available_countdown, int)
    assert api.slot_available_countdown >= 0

    assert api.slot_available_datetime is None or isinstance(
        api.slot_available_datetime, datetime
    )


@pytest.mark.parametrize(
    "status_code,exception",
    [
        (400, OverpassSyntaxError),
        (429, MultipleRequestsError),
        (504, ServerLoadError),
        (500, UnknownOverpassError),
    ],
)
def test_http_errors(status_code, exception, requests_mock):
    api = overpass.API()
    requests_mock.post(
        "https://overpass-api.de/api/interpreter",
        status_code=status_code,
        text="error",
        headers={"content-type": "text/plain"},
    )
    with pytest.raises(exception):
        api.get("node(1)")


def test_to_overpass_id():
    assert Utils.to_overpass_id(123, source="way") == 2400000123
    assert Utils.to_overpass_id(123, source="relation") == 3600000123
    with pytest.raises(ValueError):
        Utils.to_overpass_id(123, source="node")
