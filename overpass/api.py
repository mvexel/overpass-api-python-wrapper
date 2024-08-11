import csv
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import StringIO
from math import ceil
from typing import Dict, List, Optional, Tuple

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


@dataclass
class API:
    """A simple Python wrapper for the OpenStreetMap Overpass API.

    Attributes:
        timeout: The TCP connection timeout for the request.
        endpoint: URL of the Overpass interpreter.
        headers: HTTP headers to include when making requests to the Overpass endpoint.
        debug: Boolean to turn on debugging output.
        proxies: Dictionary of proxies to pass to the request library.
    """

    timeout: float = 25  # seconds
    endpoint: str = "https://overpass-api.de/api/interpreter"
    headers: Dict[str, str] = field(
        default_factory=lambda: {"Accept-Charset": "utf-8;q=0.7,*;q=0.7"}
    )
    debug: bool = False
    proxies: Optional[Dict[str, str]] = None
    _status: Optional[int] = field(init=False, default=None)

    SUPPORTED_FORMATS: List[str] = field(
        default_factory=lambda: ["geojson", "json", "xml", "csv"]
    )
    _QUERY_TEMPLATE: str = "[out:{out}]{date};{query}out {verbosity};"
    _GEOJSON_QUERY_TEMPLATE: str = "[out:json]{date};{query}out {verbosity};"

    def __post_init__(self):
        """Initialize logging if debugging is enabled."""
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    def get(
        self,
        query: str,
        responseformat: str = "geojson",
        verbosity: str = "body",
        build: bool = True,
        date: Optional[str] = "",
    ):
        """Send an Overpass query in Overpass QL.

        Args:
            query: The Overpass QL query to send to the endpoint.
            responseformat: One of the supported output formats ["geojson", "json", "xml", "csv"].
            verbosity: One of the supported levels of data verbosity ["ids", "skel", "body", "tags", "meta"].
            build: Boolean to indicate whether to build the Overpass query from a template (True) or specify full query manually (False).
            date: A date with an optional time. Example: 2020-04-27 or 2020-04-27T00:00:00Z.

        Returns:
            The response from the Overpass API in the specified format.

        Raises:
            UnknownOverpassError: If the response is invalid.
            ServerRuntimeError: If a runtime error is encountered.
        """
        if date and isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

        if build:
            full_query = self._construct_ql_query(
                query, responseformat=responseformat, verbosity=verbosity, date=date
            )
        else:
            full_query = query

        logging.info("Query: %s", query)

        r = self._get_from_overpass(full_query)
        content_type = r.headers.get("content-type")
        logging.debug("Content type: %s", content_type)

        if content_type == "text/csv":
            return list(csv.reader(StringIO(r.text), delimiter="\t"))
        elif content_type in ("text/xml", "application/xml", "application/osm3s+xml"):
            return r.text
        else:
            response = json.loads(r.text)

        if not build:
            return response

        if "elements" not in response:
            raise UnknownOverpassError("Received an invalid answer from Overpass.")

        overpass_remark = response.get("remark")
        if overpass_remark and overpass_remark.startswith("runtime error"):
            raise ServerRuntimeError(overpass_remark)

        if responseformat != "geojson":
            return response

        return json2geojson(response)

    @staticmethod
    @staticmethod
    def _api_status() -> dict:
        """Retrieve the API status.

        Returns:
            A dictionary describing the client's status with the API.
        """
        endpoint = "https://overpass-api.de/api/status"
        r = requests.get(endpoint)
        lines = r.text.splitlines()

        # Regex pattern to match the number of available slots
        available_re = re.compile(r"(\d+) slots available now.")
        available_slots = int(
            next((m.group(1) for line in lines if (m := available_re.search(line))), 0)
        )

        # Regex pattern to match waiting slots
        waiting_re = re.compile(r"Slot available after: ([\d\-TZ:]+)")
        waiting_slots = tuple(
            datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            for line in lines
            if (m := waiting_re.search(line))
        )

        # Find index of the running queries section
        current_idx = next(
            (
                i
                for i, line in enumerate(lines)
                if line.startswith("Currently running queries")
            ),
            len(lines),  # Default to end of list if not found
        )

        # Parse running queries to extract start times
        running_slots = tuple(
            datetime.strptime(slot[3], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            for line in lines[current_idx + 1 :]
            if (slot := line.split())
            and len(slot) == 4  # Ensure there are four elements in the split line
        )

        # Return the parsed status
        return {
            "available_slots": available_slots,
            "waiting_slots": waiting_slots,
            "running_slots": running_slots,
        }

    @property
    def slots_available(self) -> int:
        """Get the count of open slots the client has on the server.

        Returns:
            The number of available slots.
        """
        return self._api_status()["available_slots"]

    @property
    def slots_waiting(self) -> Tuple[datetime, ...]:
        """Get the waiting slots and when they will be available.

        Returns:
            A tuple of datetimes representing waiting slots and when they will be available.
        """
        return self._api_status()["waiting_slots"]

    @property
    def slots_running(self) -> Tuple[datetime, ...]:
        """Get the running slots and when they will be freed.

        Returns:
            A tuple of datetimes representing running slots and when they will be freed.
        """
        return self._api_status()["running_slots"]

    @property
    def slot_available_datetime(self) -> Optional[datetime]:
        """Get the datetime when the next slot will be available.

        Returns:
            None if a slot is available now (no wait needed), or a datetime representing when the next slot will become available.
        """
        if self.slots_available > 0:
            return None
        all_slots = self.slots_running + self.slots_waiting
        return min(all_slots) if all_slots else None

    @property
    def slot_available_countdown(self) -> int:
        """Get the countdown for when the next slot will be available.

        Returns:
            0 if a slot is available now, or an integer of seconds until the next slot is free.
        """
        if self.slots_available > 0:
            return 0
        if self.slot_available_datetime:
            return max(
                ceil(
                    (
                        self.slot_available_datetime - datetime.now(timezone.utc)
                    ).total_seconds()
                ),
                0,
            )
        return 0

    def search(self, feature_type, regex=False):
        """Search for a feature.

        Args:
            feature_type: The type of feature to search for.
            regex: Whether to use a regular expression for the search.

        Raises:
            NotImplementedError: The search method is not implemented.
        """
        raise NotImplementedError()

    # Deprecation of uppercase functions
    Get = get
    Search = search

    def _construct_ql_query(self, userquery, responseformat, verbosity, date):
        """Construct a full Overpass QL query.

        Args:
            userquery: The user-specified query string.
            responseformat: The format for the response.
            verbosity: The verbosity level for the response.
            date: The date for the query.

        Returns:
            The constructed query string.
        """
        raw_query = str(userquery).rstrip()
        if not raw_query.endswith(";"):
            raw_query += ";"

        date_str = f'[date:"{date:%Y-%m-%dT%H:%M:%SZ}"]' if date else ""

        template = (
            self._GEOJSON_QUERY_TEMPLATE
            if responseformat == "geojson"
            else self._QUERY_TEMPLATE
        )
        complete_query = template.format(
            query=raw_query, out=responseformat, verbosity=verbosity, date=date_str
        )

        logging.debug("Complete query: %s", complete_query)
        return complete_query

    def _get_from_overpass(self, query):
        """Send a POST request to the Overpass API.

        Args:
            query: The query to send.

        Returns:
            The HTTP response from the Overpass API.

        Raises:
            TimeoutError: If the request times out.
            OverpassSyntaxError: If the query is malformed.
            MultipleRequestsError: If too many requests are made.
            ServerLoadError: If the server is under heavy load.
            UnknownOverpassError: If an unknown error occurs.
        """
        payload = {"data": query}
        try:
            r = requests.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout,
                proxies=self.proxies,
                headers=self.headers,
            )
            r.raise_for_status()
        except requests.exceptions.Timeout:
            raise TimeoutError(self.timeout)
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, query)

        r.encoding = "utf-8"
        return r

    def _handle_http_error(self, error, query):
        """Handle HTTP errors.

        Args:
            error: The HTTP error that occurred.
            query: The query that caused the error.

        Raises:
            OverpassSyntaxError: If the query is malformed.
            MultipleRequestsError: If too many requests are made.
            ServerLoadError: If the server is under heavy load.
            UnknownOverpassError: If an unknown error occurs.
        """
        self._status = error.response.status_code
        if self._status == 400:
            raise OverpassSyntaxError(query)
        elif self._status == 429:
            raise MultipleRequestsError()
        elif self._status == 504:
            raise ServerLoadError(self.timeout)
        raise UnknownOverpassError(f"The request returned status code {self._status}")
