import sys
import requests
import json
import geojson


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    # defaults for the API class
    _timeout = 25  # seconds
    _endpoint = "http://overpass-api.de/api/interpreter"
    _responseformat = "json"
    _debug = False

    _QUERY_TEMPLATE = "[out:{responseformat}];{query}out body;"
    _GEOJSON_QUERY_TEMPLATE = "[out:json];{query}out body geom;"

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

        response = ""

        try:
            response = json.loads(self._GetFromOverpass(
                self._ConstructQLQuery(query, asGeoJSON=asGeoJSON)))
        except OverpassException as oe:
            print(oe)
            sys.exit(1)

        if "elements" not in response or len(response["elements"]) == 0:
            raise OverpassException(
                204,
                'No OSM features satisfied your query'
            )

        if not asGeoJSON:
            return response

        # construct geojson
        return self._asGeoJSON(response["elements"])

    def Search(self, feature_type, regex=False):
        """Search for something."""
        pass

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
            r = requests.get(
                self.endpoint,
                params=payload,
                timeout=self.timeout
            )
        except requests.exceptions.Timeout:
            raise OverpassException(
                408,
                'Query timed out. API instance is set to time out in {timeout}'
                ' seconds. Try passing in a higher value when instantiating'
                ' this API: api = Overpass.API(timeout=60)'.format(
                    timeout=self.timeout
                )
            )

        self._status = r.status_code

        if self._status != 200:
            if self._status == 400:
                message = 'Query syntax error'
            else:
                message = 'Error from Overpass API'
            raise OverpassException(self._status, message)
        else:
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


class OverpassException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return json.dumps({
            'status': self.status_code,
            'message': self.message
        })
