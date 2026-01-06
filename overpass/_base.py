# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

"""Shared base functionality for API and AsyncAPI classes."""

import csv
import json
import math
import re
from datetime import datetime
from io import StringIO
from typing import Any, Dict

from osm2geojson import json2geojson

from .errors import ServerRuntimeError, UnknownOverpassError

# Shared constants
SUPPORTED_FORMATS = ["geojson", "json", "xml", "csv"]

# Default configuration values
DEFAULT_TIMEOUT = 25  # seconds
DEFAULT_ENDPOINT = "https://overpass-api.de/api/interpreter"
DEFAULT_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.osm.jp/api/interpreter",
]
DEFAULT_HEADERS = {"Accept-Charset": "utf-8;q=0.7,*;q=0.7"}
DEFAULT_DEBUG = False
DEFAULT_PROXIES = None

# Query templates
QUERY_TEMPLATE = "[out:{out}]{date};{query}out {verbosity};"
GEOJSON_QUERY_TEMPLATE = "[out:json]{date};{query}out {verbosity};"


def construct_ql_query(
    userquery, responseformat: str, verbosity: str, date, debug: bool = False
) -> str:
    """Construct a complete Overpass QL query from components.

    :param userquery: The user's query string
    :param responseformat: Output format (json, xml, csv, geojson)
    :param verbosity: Output verbosity level
    :param date: Optional date/datetime for historical queries
    :param debug: If True, print the constructed query
    :return: Complete Overpass QL query string
    """
    raw_query = str(userquery).rstrip()
    if not raw_query.endswith(";"):
        raw_query += ";"

    if date:
        date = f'[date:"{date:%Y-%m-%dT%H:%M:%SZ}"]'

    if responseformat == "geojson":
        template = GEOJSON_QUERY_TEMPLATE
        complete_query = template.format(query=raw_query, verbosity=verbosity, date=date)
    else:
        template = QUERY_TEMPLATE
        complete_query = template.format(
            query=raw_query, out=responseformat, verbosity=verbosity, date=date
        )

    if debug:
        print(complete_query)
    return complete_query


def select_endpoint(endpoints: list, endpoint_index: int, rotate: bool) -> str:
    """Select an endpoint from the list based on rotation settings.

    :param endpoints: List of available endpoints
    :param endpoint_index: Current endpoint index (for rotation)
    :param rotate: Whether to rotate through endpoints
    :return: Selected endpoint URL
    """
    if not rotate or len(endpoints) == 1:
        return endpoints[0]
    endpoint = endpoints[endpoint_index % len(endpoints)]
    return endpoint


def guard_bbox(userquery, allow_large_bbox: bool, max_bbox_area_km2: float) -> None:
    """Validate that bounding boxes in the query don't exceed size limits.

    :param userquery: The user's query (string or object with bbox attributes)
    :param allow_large_bbox: If True, skip validation
    :param max_bbox_area_km2: Maximum allowed bbox area in km^2
    :raises ValueError: If a bbox exceeds the maximum allowed area
    """
    if allow_large_bbox or max_bbox_area_km2 is None:
        return

    bboxes = []
    if hasattr(userquery, "south") and hasattr(userquery, "west"):
        bboxes.append((userquery.south, userquery.west, userquery.north, userquery.east))
    else:
        bbox_re = re.compile(r"\(([-\d\.]+),([-\d\.]+),([-\d\.]+),([-\d\.]+)\)")
        for match in bbox_re.finditer(str(userquery)):
            south, west, north, east = map(float, match.groups())
            bboxes.append((south, west, north, east))

    for south, west, north, east in bboxes:
        area_km2 = bbox_area_km2(south, west, north, east)
        if area_km2 > max_bbox_area_km2:
            raise ValueError(
                f"bbox area {area_km2:.1f} km^2 exceeds limit "
                f"{max_bbox_area_km2} km^2 (set allow_large_bbox=True to override)"
            )


def bbox_area_km2(south: float, west: float, north: float, east: float) -> float:
    """Calculate the approximate area of a bounding box in square kilometers.

    :param south: Southern latitude
    :param west: Western longitude
    :param north: Northern latitude
    :param east: Eastern longitude
    :return: Area in square kilometers
    """
    mid_lat = (south + north) / 2.0
    lat_km = 111.32 * (north - south)
    lon_km = 111.32 * abs(east - west) * abs(math.cos(math.radians(mid_lat)))
    return abs(lat_km * lon_km)


def parse_csv_response(response_text: str, model: bool = False):
    """Parse CSV response from Overpass.

    :param response_text: Raw CSV response text
    :param model: If True, return a CsvResponse model instance
    :return: List of CSV rows or CsvResponse model
    """
    csv_rows = list(csv.reader(StringIO(response_text), delimiter="\t"))
    if model:
        from .models import CsvResponse

        header = csv_rows[0] if csv_rows else []
        rows = csv_rows[1:] if len(csv_rows) > 1 else []
        return CsvResponse(header=header, rows=rows)
    return csv_rows


def parse_xml_response(response_text: str, model: bool = False):
    """Parse XML response from Overpass.

    :param response_text: Raw XML response text
    :param model: If True, return an XmlResponse model instance
    :return: XML text or XmlResponse model
    """
    if model:
        from .models import XmlResponse

        return XmlResponse(text=response_text)
    return response_text


def parse_json_response(
    response_text: str, responseformat: str, build: bool, model: bool = False
) -> Any:
    """Parse and validate JSON response from Overpass.

    :param response_text: Raw JSON response text
    :param responseformat: Expected response format (json or geojson)
    :param build: Whether the query was built (affects validation)
    :param model: If True, return Pydantic model instances
    :return: Parsed JSON dict, GeoJSON dict, or model instance
    :raises UnknownOverpassError: If JSON is invalid or response is invalid
    :raises ServerRuntimeError: If Overpass reports a runtime error
    """
    try:
        response = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise UnknownOverpassError("Received a non-JSON response when JSON was expected.") from exc

    if not build:
        return response

    # Check for valid answer from Overpass.
    # A valid answer contains an 'elements' key at the root level.
    if "elements" not in response:
        raise UnknownOverpassError("Received an invalid answer from Overpass.")

    # If there is a 'remark' key, it spells trouble.
    overpass_remark = response.get("remark", None)
    if overpass_remark and overpass_remark.startswith("runtime error"):
        raise ServerRuntimeError(overpass_remark)

    if responseformat != "geojson":
        if model:
            from .models import OverpassResponse

            return OverpassResponse.model_validate(response)
        return response

    geojson_response = json2geojson(response)
    if not model:
        return geojson_response

    from .models import GeoJSONFeatureCollection

    return GeoJSONFeatureCollection.model_validate(geojson_response)
