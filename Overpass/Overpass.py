import requests
import json


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    # defaults for the API class
    _timeout = 25  # seconds
    _endpoint = "http://overpass-api.de/api/interpreter"
    _responseformat = "json"
    _debug = False
    _bbox = [-180.0, -90.0, 180.0, 90.0]

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.timeout = kwargs.get("timeout", self._timeout)
        self.responseformat = kwargs.get("responseformat", self._responseformat)
        self.debug = kwargs.get("debug", self._debug)
        self.bbox = kwargs.get("bbox", self._bbox)
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

    def Get(self, query):
        """Pass in an Overpass query in Overpass QL"""

        response = json.loads(
            self._GetFromOverpass(
                self._ConstructQLQuery(query)))

        if "elements" not in response or len(response["elements"]) == 0:
            return self._ConstructError('No OSM features satisfied your query')

        return response

    def Search(self, feature_type, regex=False):
        """Search for something."""
        pass

    def _ConstructError(self, msg):
        return {
            "status": self._status,
            "message": msg
        }

    def _ConstructQLQuery(self, userquery):
        if self.debug:
            print "[out:{responseformat}];".format(responseformat=self.responseformat) + userquery + "out body;"
        if not userquery.endswith(";"):
            userquery += ";"
        return "[out:json];" + userquery + "out body;"

    def _GetFromOverpass(self, query):
        """This sends the API request to the Overpass instance and
        returns the raw result, or an error."""

        payload = {"data": query}

        try:
            r = requests.get(self.endpoint, params=payload, timeout=self.timeout)
        except requests.exceptions.Timeout:
            return self._ConstructError(
                'Query timed out. API instance is set to time out in {timeout} seconds. '
                'Try passing in a higher value when instantiating this API:'
                'api = Overpass.API(timeout=60)'.format(timeout=self.timeout))

        self._status = r.status_code

        if self._status != 200:
            if self._status == 400:
                return self._ConstructError('Query syntax error')
            elif self._status == 500:
                return self._ConstructError('Overpass internal server error')
            else:
                return self._ConstructError('Something unexpected happened')

        return r.text
