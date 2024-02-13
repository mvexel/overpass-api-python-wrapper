# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import csv
import json
import logging
import re
from datetime import datetime, timezone
from io import StringIO
from math import ceil
from typing import Optional

import requests
from osm2geojson import json2geojson

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
            import http.client as http_client
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
        return json2geojson(response)

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
            next(
                (
                    m.group()
                    for line in lines 
                    if (m := available_re.search(line))
                ), 0
            )
        )

        waiting_re = re.compile(r'(?<=Slot available after: )[\d\-TZ:]{20}')
        waiting_slots = tuple(
            datetime.strptime(m.group(), "%Y-%m-%dT%H:%M:%S%z")
            for line in lines
            if (m := waiting_re.search(line))
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

    @property
    def slot_available_datetime(self) -> Optional[datetime]:
        """
        :returns: None if a slot is available now (no wait needed) or a datetime representing when the next slot will become available
        """
        if self.slots_available:
            return None
        return min(self.slots_running + self.slots_waiting)

    @property
    def slot_available_countdown(self) -> int:
        """
        :returns: 0 if a slot is available now, or an int of seconds until the next slot is free
        """
        try:
            return max(
                ceil(
                    (
                        self.slot_available_datetime -
                        datetime.now(timezone.utc)
                    ).total_seconds()
                ),
                0
            )
        except TypeError:
            # Can't subtract from None, which means slot is available now
            return 0

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
            date = f'[date:"{date:%Y-%m-%dT%H:%M:%SZ}"]'

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
