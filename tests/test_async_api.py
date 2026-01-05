# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

from overpass.async_api import AsyncAPI
from overpass.errors import (
    MultipleRequestsError,
    OverpassSyntaxError,
    ServerLoadError,
    UnknownOverpassError,
)
from overpass.transport import HttpxAsyncTransport


def _transport_for(handler):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return HttpxAsyncTransport(client=client)


@pytest.mark.asyncio
async def test_async_json_response():
    async def handler(request):
        return httpx.Response(
            200,
            json={"elements": [{"id": 1, "type": "node"}]},
            headers={"content-type": "application/json"},
        )

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        response = await api.get("node(1)", responseformat="json")
    assert response["elements"][0]["id"] == 1


@pytest.mark.asyncio
async def test_async_csv_response():
    async def handler(request):
        return httpx.Response(
            200,
            text="name\t@lon\t@lat\nSpringfield\t-3.0\t56.2\n",
            headers={"content-type": "text/csv"},
        )

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        response = await api.get(
            'node["name"="Springfield"]["place"]', responseformat="csv(name,::lon,::lat)"
        )
    assert response == [["name", "@lon", "@lat"], ["Springfield", "-3.0", "56.2"]]


@pytest.mark.asyncio
async def test_async_xml_response():
    async def handler(request):
        return httpx.Response(
            200,
            text="<osm><node id=\"1\" lat=\"0\" lon=\"0\" /></osm>",
            headers={"content-type": "application/osm3s+xml"},
        )

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        response = await api.get("node(1)", responseformat="xml")
    assert response.startswith("<osm>")


@pytest.mark.asyncio
async def test_async_invalid_response_raises():
    async def handler(request):
        return httpx.Response(
            200,
            json={"foo": "bar"},
            headers={"content-type": "application/json"},
        )

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        with pytest.raises(UnknownOverpassError):
            await api.get("node(1)")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,exception",
    [
        (400, OverpassSyntaxError),
        (429, MultipleRequestsError),
        (504, ServerLoadError),
        (500, UnknownOverpassError),
    ],
)
async def test_async_http_errors(status_code, exception):
    async def handler(request):
        return httpx.Response(status_code, text="error", headers={"content-type": "text/plain"})

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        with pytest.raises(exception):
            await api.get("node(1)")


@pytest.mark.asyncio
async def test_async_api_status():
    status_text = Path("tests/overpass_status/no_slots_waiting.txt").read_text()

    async def handler(request):
        if request.url.path.endswith("/api/status"):
            return httpx.Response(200, text=status_text)
        return httpx.Response(200, json={"elements": []})

    async with AsyncAPI(transport=_transport_for(handler)) as api:
        slots_available = await api.slots_available()
        slots_running = await api.slots_running()
        slots_waiting = await api.slots_waiting()
        countdown = await api.slot_available_countdown()
        slot_dt = await api.slot_available_datetime()

    assert slots_available == 2
    assert slots_running == ()
    assert slots_waiting == ()
    assert isinstance(countdown, int)
    assert slot_dt is None or isinstance(slot_dt, datetime)
