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

import httpx
from osm2geojson import json2geojson

from .errors import (
    MultipleRequestsError,
    OverpassSyntaxError,
    ServerLoadError,
    ServerRuntimeError,
    TimeoutError,
    UnknownOverpassError,
)
from .transport import HttpxAsyncTransport


class AsyncAPI:
    """Async wrapper for the OpenStreetMap Overpass API.

    :param timeout: If a single number, the TCP connection timeout for the request. If a tuple
                    of two numbers, the connection timeout and the read timeout respectively.
                    Timeouts can be integers or floats.
    :param endpoint: URL of overpass interpreter
    :param headers: HTTP headers to include when making requests to the overpass endpoint
    :param debug: Boolean to turn on debugging output
    :param proxies: Dictionary of proxies to pass to the request library.
    :param transport: Optional async transport instance for HTTP requests.
    """

    SUPPORTED_FORMATS = ["geojson", "json", "xml", "csv"]

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
        self.transport = kwargs.get("transport") or HttpxAsyncTransport(
            proxies=self.proxies, headers=self.headers
        )
        self._status = None

        if self.debug:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)

    async def __aenter__(self) -> "AsyncAPI":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if hasattr(self.transport, "aclose"):
            await self.transport.aclose()

    async def get(
        self,
        query,
        responseformat="geojson",
        verbosity="body",
        build=True,
        date="",
        model: bool = False,
    ):
        """Pass in an Overpass query in Overpass QL (async)."""
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
        if self.debug:
            logging.getLogger().info(query)

        r = await self._get_from_overpass(full_query)
        content_type = r.headers.get("content-type")

        if self.debug:
            print(content_type)
        if content_type == "text/csv":
            return list(csv.reader(StringIO(r.text), delimiter="\t"))
        elif content_type in ("text/xml", "application/xml", "application/osm3s+xml"):
            return r.text
        else:
            try:
                response = json.loads(r.text)
            except json.JSONDecodeError as exc:
                raise UnknownOverpassError(
                    "Received a non-JSON response when JSON was expected."
                ) from exc

        if not build:
            return response

        if "elements" not in response:
            raise UnknownOverpassError("Received an invalid answer from Overpass.")

        overpass_remark = response.get("remark", None)
        if overpass_remark and overpass_remark.startswith("runtime error"):
            raise ServerRuntimeError(overpass_remark)

        if responseformat != "geojson":
            if model:
                from .models import OverpassResponse

                return OverpassResponse.model_validate(response)
            return response

        geojson_response = json2geojson(response)
        if not model:
            return geojson_response

        from .models import GeoJSONFeatureCollection

        return GeoJSONFeatureCollection.model_validate(geojson_response)

    async def _api_status(self) -> dict:
        endpoint = "https://overpass-api.de/api/status"

        r = await self.transport.get(
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

    async def slots_available(self) -> int:
        return (await self._api_status())["available_slots"]

    async def slots_waiting(self) -> tuple:
        return (await self._api_status())["waiting_slots"]

    async def slots_running(self) -> tuple:
        return (await self._api_status())["running_slots"]

    async def slot_available_datetime(self) -> Optional[datetime]:
        if await self.slots_available():
            return None
        return min((await self.slots_running()) + (await self.slots_waiting()))

    async def slot_available_countdown(self) -> int:
        try:
            return max(
                ceil((await self.slot_available_datetime() - datetime.now(timezone.utc)).total_seconds()),
                0,
            )
        except TypeError:
            return 0

    def _construct_ql_query(self, userquery, responseformat, verbosity, date):
        raw_query = str(userquery).rstrip()
        if not raw_query.endswith(";"):
            raw_query += ";"

        if date:
            date = f'[date:"{date:%Y-%m-%dT%H:%M:%SZ}"]'

        if responseformat == "geojson":
            template = self._GEOJSON_QUERY_TEMPLATE
            complete_query = template.format(query=raw_query, verbosity=verbosity, date=date)
        else:
            template = self._QUERY_TEMPLATE
            complete_query = template.format(
                query=raw_query, out=responseformat, verbosity=verbosity, date=date
            )

        if self.debug:
            print(complete_query)
        return complete_query

    async def _get_from_overpass(self, query):
        payload = {"data": query}

        try:
            r = await self.transport.post(
                self.endpoint,
                data=payload,
                timeout=self.timeout,
                proxies=self.proxies,
                headers=self.headers,
            )
        except httpx.TimeoutException:
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
