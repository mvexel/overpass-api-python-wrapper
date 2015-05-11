import json
import re

import geojson
import requests

from .errors import OverpassSyntaxError, TimeoutError, MultipleRequestsError
from .errors import ServerLoadError, UnknownOverpassError


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    # defaults for the API class
    _timeout = 25  # seconds
    _endpoint = "http://overpass-api.de/api/interpreter"
    _responseformat = "json"
    _debug = False

    _QUERY_TEMPLATE = "[out:{responseformat}];{query}out body;"
    _GEOJSON_QUERY_TEMPLATE = "[out:json];{query}out body;>;out skel qt;"

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.timeout = kwargs.get("timeout", self._timeout)
        self.responseformat = kwargs.get(
            "responseformat",
            self._responseformat
        )
        self.debug = kwargs.get("debug", self._debug)
        self._status = None

        if self.debug:
            import httplib
            import logging
            httplib.HTTPConnection.debuglevel = 1

            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def Get(self, query, asGeoJSON=False):
        """Pass in an Overpass query in Overpass QL"""

        full_query = self._ConstructQLQuery(query, asGeoJSON=asGeoJSON)
        raw_response = self._GetFromOverpass(full_query)
        response = json.loads(raw_response)

        if "elements" not in response:
            raise UnknownOverpassError("Received an invalid answer from Overpass.")

        if not asGeoJSON:
            return response

        # construct geojson
        return self._asGeoJSON(response["elements"])

    def Search(self, feature_type, regex=False):
        """Search for something."""
        raise NotImplementedError()

    def _ConstructQLQuery(self, userquery, asGeoJSON=False):
        raw_query = str(userquery)
        if not raw_query.endswith(";"):
            raw_query += ";"

        if asGeoJSON:
            template = self._GEOJSON_QUERY_TEMPLATE
        else:
            template = self._QUERY_TEMPLATE

        complete_query = template.format(
            responseformat=self.responseformat,
            query=raw_query)

        if self.debug:
            print(complete_query)
        return complete_query

    def _GetFromOverpass(self, query):
        """This sends the API request to the Overpass instance and
        returns the raw result, or an error."""

        payload = {"data": query}

        try:
            r = requests.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout
            )

        except requests.exceptions.Timeout:
            raise TimeoutError(self._timeout)

        self._status = r.status_code

        if self._status != 200:
            if self._status == 400:
                error_msgs = list(re.findall("line [0-9]+:[^<]+", r.content))
                raise OverpassSyntaxError(query, "\n".join(error_msgs))
            elif self._status == 429:
                raise MultipleRequestsError()
            elif self._status == 504:
                raise ServerLoadError(self._timeout)
            raise UnknownOverpassError(
                "The request returned status code {code}".format(
                    code=self._status
                    )
                )
        else:
            return r.text

    def _asGeoJSON(self, elements):
        #print 'DEB _asGeoJson elements:', elements

        def makeFeature(elem, geometry):
            return geojson.Feature(
                id=elem["id"],
                geometry=geometry,
                properties=elem.get("tags"))

        ignore_ids = set()
        features = {}

        def collectFeatures():
            # 1. Collect all points
            for elem in elements:
                elem_type = elem["type"]
                if elem_type == "node":
                    yield makeFeature(elem, geojson.Point((elem["lon"], elem["lat"])))

            # 2. Collect all ways
            for elem in elements:
                elem_type = elem["type"]
                osm_geom_type = elem.get("tags", {}).get("type", "")

                if elem_type == "way":
                    points = []
                    if elem.has_key("geometry"):
                        for coords in elem["geometry"]:
                            points.append((coords["lon"], coords["lat"]))
                    if elem.has_key("nodes"):
                        for node_id in elem["nodes"]:
                            if features.has_key(node_id):
                                geom = features[node_id].geometry
                                points.append(geom['coordinates'])
                                # since we have "consumed" this point, do not return it
                                ignore_ids.add(node_id)
                    if points[0] == points[-1] or osm_geom_type == 'polygon':
                        yield makeFeature(elem, geojson.Polygon([points]))
                    else:
                        yield makeFeature(elem, geojson.LineString(points))

            # 3. Collect all relations
            for elem in elements:
                elem_type = elem["type"]
                osm_geom_type = elem.get("tags", {}).get("type", "")

                if elem_type == "relation":
                    if osm_geom_type == "multipolygon":
                        ways = []

                        if elem.has_key("members"):
                            for member in elem["members"]:
                                if member["type"] == "way":
                                    way_points = []
                                    if member.has_key("ref") and features.has_key(member["ref"]):
                                        way_id = member["ref"]
                                        if type(features[way_id].geometry) == geojson.geometry.Polygon:
                                            ways.append(features[way_id].geometry)
                                        # since we have "consumed" this way, do not return it
                                        ignore_ids.add(way_id)
                                    if member.has_key("geometry"):
                                        for coords in member["geometry"]:
                                            way_points.append((coords["lon"], coords["lat"]))
                                        ways.append(geojson.Polygon([way_points]))
                        yield makeFeature(elem, geojson.MultiPolygon([way_geom["coordinates"] for way_geom in ways]))
                    else:
                        ways = []

                        if elem.has_key("members"):
                            for member in elem["members"]:
                                if member["type"] == "way":
                                    way_points = []
                                    if member.has_key("ref") and features.has_key(member["ref"]):
                                        way_id = member["ref"]
                                        if type(features[way_id].geometry) == geojson.geometry.LineString:
                                            ways.append(features[way_id].geometry)
                                        # since we have "consumed" this way, do not return it
                                        ignore_ids.add(way_id)
                                    if member.has_key("geometry"):
                                        for coords in member["geometry"]:
                                            way_points.append((coords["lon"], coords["lat"]))
                                        ways.append(geojson.LineString(way_points))
                        yield makeFeature(elem, geojson.MultiLineString([way_geom["coordinates"] for way_geom in ways]))

        for feature in collectFeatures():
            features[feature.id] = feature

        return geojson.FeatureCollection([v for (k, v) in features.items() if not k in ignore_ids])
