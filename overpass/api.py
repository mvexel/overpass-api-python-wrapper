# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import csv
import json
import logging
import re
from datetime import datetime
from io import StringIO

import geojson
import requests
from shapely.geometry import Point, Polygon

from .errors import (
    MultipleRequestsError,
    OverpassSyntaxError,
    ServerLoadError,
    ServerRuntimeError,
    TimeoutError,
    UnknownOverpassError,
)


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API.

    :param timeout: If a single number, the TCP connection timeout for the request. If a tuple
                    of two numbers, the connection timeout and the read timeout respectively.
                    Timeouts can be integers or floats.
    :param endpoint: URL of overpass interpreter
    :param headers: HTTP headers to include when making requests to the overpass endpoint
    :param debug: Boolean to turn on debugging output
    :param proxies: Dictionary of proxies to pass to the request library. See
                    requests documentation for details.
    """

    SUPPORTED_FORMATS = ["geojson", "json", "xml", "csv"]

    # defaults for the API class
    _timeout = 25  # second
    _endpoint = "https://overpass-api.de/api/interpreter"
    _headers = {"Accept-Charset": "utf-8;q=0.7,*;q=0.7"}
    _debug = False
    _proxies = None

    _QUERY_TEMPLATE = "[out:{out}]{date};{query}out {verbosity};"
    _GEOJSON_QUERY_TEMPLATE = "[out:json]{date};{query}out {verbosity};"

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.headers = kwargs.get("headers", self._headers)
        self.timeout = kwargs.get("timeout", self._timeout)
        self.debug = kwargs.get("debug", self._debug)
        self.proxies = kwargs.get("proxies", self._proxies)
        self._status = None

        if self.debug:
            # https://stackoverflow.com/a/16630836
            try:
                import http.client as http_client
            except ImportError:
                # Python 2
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1

            # You must initialize logging,
            # otherwise you'll not see debug output.
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def get(self, query, responseformat="geojson", verbosity="body", build=True, date=''):
        """Pass in an Overpass query in Overpass QL.

        :param query: the Overpass QL query to send to the endpoint
        :param responseformat: one of the supported output formats ["geojson", "json", "xml", "csv"]
        :param verbosity: one of the supported levels out data verbosity ["ids",
                          "skel", "body", "tags", "meta"] and optionally modifiers ["geom", "bb",
                          "center"] followed by an optional sorting indicator ["asc", "qt"]. Example:
                          "body geom qt"
        :param build: boolean to indicate whether to build the overpass query from a template (True)
                          or allow the programmer to specify full query manually (False)
        :param date: a date with an optional time. Example: 2020-04-27 or 2020-04-27T00:00:00Z
        """
        if date and isinstance(date, str):
            # If date is given and is not already a datetime, attempt to parse from string
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                # The 'Z' in a standard overpass date will throw fromisoformat() off
                date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        # Construct full Overpass query
        if build:
            full_query = self._construct_ql_query(
                query, responseformat=responseformat, verbosity=verbosity, date=date
            )
        else:
            full_query = query
        if self.debug:
            logging.getLogger().info(query)

        # Get the response from Overpass
        r = self._get_from_overpass(full_query)
        content_type = r.headers.get("content-type")

        if self.debug:
            print(content_type)
        if content_type == "text/csv":
            return list(csv.reader(StringIO(r.text), delimiter="\t"))
        elif content_type in ("text/xml", "application/xml", "application/osm3s+xml"):
            return r.text
        else:
            response = json.loads(r.text)

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
            return response

        # construct geojson
        return self._as_geojson(response["elements"])

    @staticmethod
    def _api_status() -> dict:
        """
        :returns: dict describing the client's status with the API
        """
        endpoint = "https://overpass-api.de/api/status"

        r = requests.get(endpoint)
        lines = tuple(r.text.splitlines())

        available_re = re.compile(r'\d(?= slots? available)')
        available_slots = int(
            available_re.search(lines[3]).group()
            if available_re.search(lines[3])
            else 0
        )

        waiting_re = re.compile(r'(?<=Slot available after: )[\d\-TZ:]{20}')
        waiting_slots = tuple(
            datetime.strptime(
                waiting_re.search(line).group(), "%Y-%m-%dT%H:%M:%S%z"
            )
            for line in lines if waiting_re.search(line)
        )

        current_idx = next(
            i for i, word in enumerate(lines)
            if word.startswith('Currently running queries')
        )
        running_slots = tuple(tuple(line.split()) for line in lines[current_idx + 1:])
        running_slots_datetimes = tuple(
            datetime.strptime(
                slot[3], "%Y-%m-%dT%H:%M:%S%z"
            )
            for slot in running_slots
        )

        return {
            "available_slots": available_slots,
            "waiting_slots": waiting_slots,
            "running_slots": running_slots_datetimes,
        }

    @property
    def slots_available(self) -> int:
        """
        :returns: count of open slots the client has on the server
        """
        return self._api_status()["available_slots"]

    @property
    def slots_waiting(self) -> tuple:
        """
        :returns: tuple of datetimes representing waiting slots and when they will be available
        """
        return self._api_status()["waiting_slots"]

    @property
    def slots_running(self) -> tuple:
        """
        :returns: tuple of datetimes representing running slots and when they will be freed
        """
        return self._api_status()["running_slots"]

    def search(self, feature_type, regex=False):
        """Search for something."""
        raise NotImplementedError()

    # deprecation of upper case functions
    Get = get
    Search = search

    def _construct_ql_query(self, userquery, responseformat, verbosity, date):
        raw_query = str(userquery).rstrip()
        if not raw_query.endswith(";"):
            raw_query += ";"

        if date:
            date = f'[date:"{date.strftime("%Y-%m-%dT%H:%M:%SZ")}"]'

        if responseformat == "geojson":
            template = self._GEOJSON_QUERY_TEMPLATE
            complete_query = template.format(
                query=raw_query, verbosity=verbosity, date=date)
        else:
            template = self._QUERY_TEMPLATE
            complete_query = template.format(
                query=raw_query, out=responseformat, verbosity=verbosity, date=date
            )

        if self.debug:
            print(complete_query)
        return complete_query

    def _get_from_overpass(self, query):
        payload = {"data": query}

        try:
            r = requests.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout,
                proxies=self.proxies,
                headers=self.headers,
            )

        except requests.exceptions.Timeout:
            raise TimeoutError(self._timeout)

        self._status = r.status_code

        if self._status != 200:
            if self._status == 400:
                raise OverpassSyntaxError(query)
            elif self._status == 429:
                raise MultipleRequestsError()
            elif self._status == 504:
                raise ServerLoadError(self._timeout)
            raise UnknownOverpassError(
                "The request returned status code {code}".format(code=self._status)
            )
        else:
            r.encoding = "utf-8"
            return r

    def _as_geojson(self, elements):
        ids_already_seen = set()
        features = []
        geometry = None
        for elem in elements:
            try:
                if elem["id"] in ids_already_seen:
                    continue
                ids_already_seen.add(elem["id"])
            except KeyError:
                raise UnknownOverpassError("Received corrupt data from Overpass (no id).")
            elem_type = elem.get("type")
            elem_tags = elem.get("tags")
            elem_nodes = elem.get("nodes", None)
            elem_timestamp = elem.get("timestamp", None)
            elem_user = elem.get("user", None)
            elem_uid = elem.get("uid", None)
            elem_version = elem.get("version", None)
            if elem_nodes:
                elem_tags["nodes"] = elem_nodes
            if elem_user:
                elem_tags["user"] = elem_user
            if elem_uid:
                elem_tags["uid"] = elem_uid  
            if elem_version:
                elem_tags["version"] = elem_version                                                
            elem_geom = elem.get("geometry", [])
            if elem_type == "node":
                # Create Point geometry
                geometry = geojson.Point((elem.get("lon"), elem.get("lat")))
            elif elem_type == "way":
                # Create LineString geometry
                geometry = geojson.LineString([(coords["lon"], coords["lat"]) for coords in elem_geom])
            elif elem_type == "relation":
                # Initialize polygon list
                polygons = []
                # First obtain the outer polygons
                for member in elem.get("members", []):
                    if member["role"] == "outer":
                        points = [(coords["lon"], coords["lat"]) for coords in member.get("geometry", [])]
                        # Check that the outer polygon is complete
                        if points and points[-1] == points[0]:
                            polygons.append([points])
                        else:
                            raise UnknownOverpassError("Received corrupt data from Overpass (incomplete polygon).")
                # Then get the inner polygons
                for member in elem.get("members", []):
                    if member["role"] == "inner":
                        points = [(coords["lon"], coords["lat"]) for coords in member.get("geometry", [])]
                        # Check that the inner polygon is complete
                        if not points or points[-1] != points[0]:
                            raise UnknownOverpassError("Received corrupt data from Overpass (incomplete polygon).")
                        # We need to check to which outer polygon the inner polygon belongs
                        point = Point(points[0])
                        for poly in polygons:
                            polygon = Polygon(poly[0])
                            if polygon.contains(point):
                                poly.append(points)
                                break
                        else:
                            raise UnknownOverpassError("Received corrupt data from Overpass (inner polygon cannot "
                                                       "be matched to outer polygon).")
                # Finally create MultiPolygon geometry
                if polygons:
                    geometry = geojson.MultiPolygon(polygons)
            else:
                raise UnknownOverpassError("Received corrupt data from Overpass (invalid element).")

            if geometry:
                feature = geojson.Feature(
                    id=elem["id"],
                    geometry=geometry,
                    properties=elem_tags
                )
                features.append(feature)

        return geojson.FeatureCollection(features)
