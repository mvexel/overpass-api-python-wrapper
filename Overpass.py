import requests
import json


class API(object):
    """A simple Python wrapper for the OpenStreetMap Overpass API"""

    # defaults for the API class
    TIMEOUT = 25  # seconds
    ENDPOINT = "http://overpass-api.de/api/interpreter"

    def __init__(self,
                 endpoint=None,
                 timeout=None,
                 ):
        if endpoint is None:
            self.endpoint = self.ENDPOINT
        else:
            self.endpoint = endpoint
        if timeout is None:
            self.timeout = self.TIMEOUT
        else:
            self.timeout = timeout
        self.status = None

    def Get(self, query):
        """Pass in an Overpass query in Overpass XML or Overpass QL"""

        payload = {"data": query}

        try:
            r = requests.get(self.endpoint, params=payload, timeout=self.timeout)
        except requests.exceptions.Timeout:
            return self._ConstructError(
                'Query timed out. API instance is set to time out in {timeout} seconds. '
                'Try passing in a higher value when instantiating this API:'
                'api = Overpass.API(timeout=60)'.format(timeout=self.timeout))

        self.status = r.status_code

        if self.status != 200:
            if self.status == 400:
                return self._ConstructError('Query syntax error')
            elif self.status == 500:
                return self._ConstructError('Overpass internal server error')

        response = json.loads(r.text)

        if "elements" not in response or len(response["elements"]) == 0:
            return self._ConstructError('No OSM features satisfied your query')

        return response

    def _ConstructError(self, msg):
        return {
            "status": self.status,
            "message": msg
        }
