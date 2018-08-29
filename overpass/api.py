# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import requests
import json
import csv
import geojson
import logging
from io import StringIO
from .errors import (
    OverpassSyntaxError,
    TimeoutError,
    MultipleRequestsError,
    ServerLoadError,
    UnknownOverpassError,
    ServerRuntimeError,
)


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API."""

    SUPPORTED_FORMATS = ["geojson", "json", "xml", "csv"]

    # defaults for the API class
    _timeout = 25  # second
    _endpoint = "https://overpass-api.de/api/interpreter"
    _debug = False
    _proxies = None

    _QUERY_TEMPLATE = "[out:{out}];{query}out {verbosity};"
    _GEOJSON_QUERY_TEMPLATE = "[out:json];{query}out {verbosity};"

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
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

    def get(self, query, responseformat="geojson", verbosity="body", build=True):
        """Pass in an Overpass query in Overpass QL."""
        # Construct full Overpass query
        if build:
            full_query = self._construct_ql_query(
                query, responseformat=responseformat, verbosity=verbosity
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
            result = []
            reader = csv.reader(StringIO(r.text), delimiter="\t")
            for row in reader:
                result.append(row)
            return result
        elif content_type in ("text/xml", "application/xml", "application/osm3s+xml"):
            return r.text
        elif content_type == "application/json":
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

        if responseformat is not "geojson":
            return response

        # construct geojson
        return self._as_geojson(response["elements"])

    def search(self, feature_type, regex=False):
        """Search for something."""
        raise NotImplementedError()

    # deprecation of upper case functions
    Get = get
    Search = search

    def _construct_ql_query(self, userquery, responseformat, verbosity):
        raw_query = str(userquery).rstrip()
        if not raw_query.endswith(";"):
            raw_query += ";"

        if responseformat == "geojson":
            template = self._GEOJSON_QUERY_TEMPLATE
            complete_query = template.format(query=raw_query, verbosity=verbosity)
        else:
            template = self._QUERY_TEMPLATE
            complete_query = template.format(
                query=raw_query, out=responseformat, verbosity=verbosity
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
                headers={"Accept-Charset": "utf-8;q=0.7,*;q=0.7"},
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

        features = []
        geometry = None
        for elem in elements:
            elem_type = elem.get("type")
            if elem_type and elem_type == "node":
                geometry = geojson.Point((elem.get("lon"), elem.get("lat")))
            elif elem_type and elem_type == "way":
                points = []
                geom = elem.get("geometry")
                if geom:
                    for coords in elem.get("geometry"):
                        points.append((coords["lon"], coords["lat"]))
                    geometry = geojson.LineString(points)
            else:
                continue

            feature = geojson.Feature(
                id=elem["id"], geometry=geometry, properties=elem.get("tags")
            )
            features.append(feature)

        return geojson.FeatureCollection(features)
