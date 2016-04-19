import requests
import json
import geojson

from .errors import (OverpassSyntaxError, TimeoutError, MultipleRequestsError,
                     ServerLoadError, UnknownOverpassError, ServerRuntimeError)


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    SUPPORTED_FORMATS = ["geojson", "json", "xml"]

    # defaults for the API class
    _timeout = 25  # seconds
    _endpoint = "http://overpass-api.de/api/interpreter"
    _debug = False
    _limit = ""
    _headers = {'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}

    _QUERY_TEMPLATE = u"[out:{out}];{query}out {limit} {verbosity};"
    _GEOJSON_QUERY_TEMPLATE = u"[out:json];{query}out {limit} body geom;"

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.timeout = kwargs.get("timeout", self._timeout)
        self.debug = kwargs.get("debug", self._debug)
        self.limit = kwargs.get("limit", self._limit)
        self.headers = self._headers.update(kwargs.get("headers", {}))
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

    def Get(self, query, responseformat="geojson", verbosity="body"):
        """Pass in an Overpass query in Overpass QL"""

        # Construct full Overpass query
        full_query = self._ConstructQLQuery(query, responseformat=responseformat, verbosity=verbosity)

        # Get the response from Overpass
        raw_response = self._GetFromOverpass(full_query)

        if responseformat == "xml":
            return raw_response

        response = json.loads(raw_response)

        # Check for valid answer from Overpass. A valid answer contains an 'elements' key at the root level.
        if "elements" not in response:
            raise UnknownOverpassError("Received an invalid answer from Overpass.")

        # If there is a 'remark' key, it spells trouble.
        overpass_remark = response.get('remark', None)
        if overpass_remark and overpass_remark.startswith('runtime error'):
            raise ServerRuntimeError(overpass_remark)

        if responseformat is not "geojson":
            return response

        # construct geojson
        return self._asGeoJSON(response["elements"])

    def Search(self, feature_type, regex=False):
        """Search for something."""
        raise NotImplementedError()

    def _ConstructQLQuery(self, userquery, responseformat, verbosity):
        if not userquery.strip().endswith(";"):
            userquery += ";"

        if responseformat == "geojson":
            template = self._GEOJSON_QUERY_TEMPLATE
            complete_query = template.format(query=userquery, verbosity=verbosity, limit=self.limit)
        else:
            template = self._QUERY_TEMPLATE
            complete_query = template.format(query=userquery, out=responseformat, verbosity=verbosity, limit=self.limit)

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
                timeout=self.timeout,
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
                "The request returned status code {code}".format(
                    code=self._status
                )
            )
        else:
            r.encoding = 'utf-8'
            return r.text

    def _asGeoJSON(self, elements):

        features = []
        for elem in elements:
            elem_type = elem["type"]
            if elem_type == "node":
                geometry = geojson.Point((elem["lon"], elem["lat"]))
            elif elem_type == "way":
                points = []
                for coords in elem["geometry"]:
                    points.append((coords["lon"], coords["lat"]))
                geometry = geojson.LineString(points)
            else:
                continue

            feature = geojson.Feature(
                id=elem["id"],
                geometry=geometry,
                properties=elem.get("tags"))
            features.append(feature)

        return geojson.FeatureCollection(features)
