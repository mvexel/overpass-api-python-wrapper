import requests
import json
import geojson

from .errors import (OverpassSyntaxError, TimeoutError, MultipleRequestsError,
                     ServerLoadError, UnknownOverpassError, ServerRuntimeError)

class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    # defaults for the API class
    _timeout = 25  # seconds
    _endpoint = "http://overpass-api.de/api/interpreter"
    _debug = False

    _XML_QUERY_TEMPLATE = "[out:xml]{query}out body;"
    _JSON_QUERY_TEMPLATE = "[out:json]{query}out body;"
    _GEOJSON_QUERY_TEMPLATE = "[out:json];{query}out body geom;"

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.timeout = kwargs.get("timeout", self._timeout)
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

        # Construct full Overpass query
        full_query = self._ConstructQLQuery(query, asGeoJSON=asGeoJSON)
        
        print("full query: ", full_query)

        # Get the response from Overpass
        raw_response = self._GetFromOverpass(full_query)

        print("raw response: ", raw_response)

        response = json.loads(raw_response)

        # Check for valid answer from Overpass. A valid answer contains an 'elements' key at the root level.
        if "elements" not in response:
            raise UnknownOverpassError("Received an invalid answer from Overpass.")

        # If there is a 'remark' key, it spells trouble.
        overpass_remark = response.get('remark', None)
        if overpass_remark and overpass_remark.startswith('runtime error'):
            raise ServerRuntimeError(overpass_remark)

        if not asGeoJSON:
            return response

        # construct geojson
        return self._asGeoJSON(response["elements"])

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
            template = self._JSON_QUERY_TEMPLATE

        complete_query = template.format(query=raw_query)

        if self.debug:
            print(complete_query)
        return complete_query

    def _GetFromOverpass(self, query):
        """This sends the API request to the Overpass instance and
        returns the raw result, or an error."""

        print("query: ", query)

        payload = {"data": query}

        try:
            r = requests.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout,
                headers={'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}
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
        #print 'DEB _asGeoJson elements:', elements

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
