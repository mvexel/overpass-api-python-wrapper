# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import logging
import re
import time
from datetime import datetime, timezone
from math import ceil
from typing import Any, Optional

import requests

from ._base import (
    DEFAULT_DEBUG,
    DEFAULT_ENDPOINT,
    DEFAULT_ENDPOINTS,
    DEFAULT_HEADERS,
    DEFAULT_PROXIES,
    DEFAULT_TIMEOUT,
    SUPPORTED_FORMATS,
    bbox_area_km2,
    construct_ql_query,
    guard_bbox,
    parse_csv_response,
    parse_json_response,
    parse_xml_response,
    select_endpoint,
)
from .errors import (
    MultipleRequestsError,
    OverpassSyntaxError,
    ServerLoadError,
    ServerRuntimeError,
    TimeoutError,
    UnknownOverpassError,
)
from .transport import RequestsTransport


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
    :param transport: Optional transport instance for HTTP requests.
    """

    SUPPORTED_FORMATS = SUPPORTED_FORMATS

    # defaults for the API class
    _timeout = DEFAULT_TIMEOUT
    _endpoint = DEFAULT_ENDPOINT
    _default_endpoints = DEFAULT_ENDPOINTS
    _headers = DEFAULT_HEADERS
    _debug = DEFAULT_DEBUG
    _proxies = DEFAULT_PROXIES

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.get("endpoint", self._endpoint)
        self.headers = kwargs.get("headers", self._headers)
        self.timeout = kwargs.get("timeout", self._timeout)
        self.debug = kwargs.get("debug", self._debug)
        self.proxies = kwargs.get("proxies", self._proxies)
        self.transport = kwargs.get("transport") or RequestsTransport()
        if kwargs.get("endpoints") is not None:
            self.endpoints = kwargs.get("endpoints")
        elif kwargs.get("fallback"):
            self.endpoints = self._default_endpoints
        else:
            self.endpoints = [self.endpoint]
        self.rotate = kwargs.get("rotate", False)
        self.fallback = kwargs.get("fallback", False)
        self.max_retries = kwargs.get("max_retries", 0)
        self.min_retry_delay = kwargs.get("min_retry_delay", 10)
        self.allow_large_bbox = kwargs.get("allow_large_bbox", False)
        self.max_bbox_area_km2 = kwargs.get("max_bbox_area_km2", 1000.0)
        self._endpoint_index = 0
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

    def get(
        self,
        query,
        responseformat="geojson",
        verbosity="body",
        build=True,
        date="",
        model: bool = False,
    ):
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
                date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        # Construct full Overpass query
        if build:
            guard_bbox(query, self.allow_large_bbox, self.max_bbox_area_km2)
            full_query = construct_ql_query(
                query,
                responseformat=responseformat,
                verbosity=verbosity,
                date=date,
                debug=self.debug,
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
            return parse_csv_response(r.text, model=model)
        elif content_type in ("text/xml", "application/xml", "application/osm3s+xml"):
            return parse_xml_response(r.text, model=model)
        else:
            return parse_json_response(
                r.text, responseformat=responseformat, build=build, model=model
            )

    def _api_status(self) -> dict:
        """
        :returns: dict describing the client's status with the API
        """
        # Derive status endpoint from configured endpoint
        from urllib.parse import urlparse

        parsed = urlparse(self.endpoints[0])
        path_parts = parsed.path.rstrip("/").rsplit("/", 1)
        if len(path_parts) > 1:
            status_path = f"{path_parts[0]}/status"
        else:
            status_path = "/api/status"
        endpoint = f"{parsed.scheme}://{parsed.netloc}{status_path}"

        r = self.transport.get(
            endpoint,
            timeout=None,
            proxies=self.proxies,
            headers=self.headers,
        )
        lines = tuple(r.text.splitlines())

        available_re = re.compile(r"\d(?= slots? available)")
        available_slots = int(
            next((m.group() for line in lines if (m := available_re.search(line))), 0)
        )

        waiting_re = re.compile(r"(?<=Slot available after: )[\d\-TZ:]{20}")
        waiting_slots = tuple(
            datetime.strptime(m.group(), "%Y-%m-%dT%H:%M:%S%z")
            for line in lines
            if (m := waiting_re.search(line))
        )

        current_idx = next(
            i for i, word in enumerate(lines) if word.startswith("Currently running queries")
        )
        running_slots = tuple(tuple(line.split()) for line in lines[current_idx + 1 :])
        running_slots_datetimes = tuple(
            datetime.strptime(slot[3], "%Y-%m-%dT%H:%M:%S%z") for slot in running_slots
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
                ceil((self.slot_available_datetime - datetime.now(timezone.utc)).total_seconds()), 0
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

    def _get_from_overpass(self, query):
        payload = {"data": query}

        attempts = 0
        endpoints = (
            self.endpoints
            if self.fallback
            else [select_endpoint(self.endpoints, self._endpoint_index, self.rotate)]
        )
        if not self.fallback and self.rotate:
            self._endpoint_index += 1

        while True:
            endpoint = endpoints[min(attempts, len(endpoints) - 1)]
            try:
                r = self.transport.post(
                    endpoint,
                    data=payload,
                    timeout=self.timeout,
                    proxies=self.proxies,
                    headers=self.headers,
                )
            except requests.exceptions.Timeout:
                if attempts >= self.max_retries:
                    raise TimeoutError(self._timeout)
                time.sleep(max(self.min_retry_delay, 10))
                attempts += 1
                continue

            self._status = r.status_code

            if self._status != 200:
                if self._status == 400:
                    raise OverpassSyntaxError(query)
                elif self._status == 429:
                    if attempts >= self.max_retries:
                        raise MultipleRequestsError()
                    time.sleep(max(self.min_retry_delay, 10))
                    attempts += 1
                    continue
                elif self._status == 504:
                    if attempts >= self.max_retries:
                        raise ServerLoadError(self._timeout)
                    time.sleep(max(self.min_retry_delay, 10))
                    attempts += 1
                    continue
                raise UnknownOverpassError(
                    "The request returned status code {code}".format(code=self._status)
                )
            else:
                r.encoding = "utf-8"
                return r
