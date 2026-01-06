# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable

import httpx
import requests


@runtime_checkable
class Transport(Protocol):
    """Protocol defining the synchronous transport interface.

    This protocol ensures type safety for sync transport implementations.
    Any class implementing these methods can be used as a transport layer.
    """

    def get(
        self,
        url: str,
        *,
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> requests.Response:
        """Perform a GET request."""
        ...

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> requests.Response:
        """Perform a POST request."""
        ...


@runtime_checkable
class AsyncTransport(Protocol):
    """Protocol defining the asynchronous transport interface.

    This protocol ensures type safety for async transport implementations.
    Any class implementing these methods can be used as an async transport layer.
    """

    async def get(
        self,
        url: str,
        *,
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> httpx.Response:
        """Perform an async GET request."""
        ...

    async def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> httpx.Response:
        """Perform an async POST request."""
        ...

    async def aclose(self) -> None:
        """Close the async transport and release resources."""
        ...


class RequestsTransport:
    """Synchronous HTTP transport using the requests library."""

    def get(
        self,
        url: str,
        *,
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> requests.Response:
        return requests.get(url, timeout=timeout, proxies=proxies, headers=headers)

    def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> requests.Response:
        return requests.post(url, data=data, timeout=timeout, proxies=proxies, headers=headers)


class HttpxAsyncTransport:
    """Asynchronous HTTP transport using the httpx library.

    Note: The proxies parameter in get() and post() methods is ignored.
    Proxies should be configured via the __init__ method or by providing
    a pre-configured httpx.AsyncClient.
    """

    def __init__(
        self,
        client: Optional[httpx.AsyncClient] = None,
        *,
        proxies: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> None:
        """Initialize the async transport.

        Args:
            client: Optional pre-configured httpx.AsyncClient.
            proxies: Proxy configuration dict. Only used if client is None.
            headers: Default headers dict. Only used if client is None.
        """
        if client is None:
            # Convert proxies dict to httpx format if needed
            proxy = None
            if proxies:
                if isinstance(proxies, dict):
                    proxy = proxies.get("https") or proxies.get("http")
                else:
                    proxy = proxies

            self._client = httpx.AsyncClient(headers=headers, proxy=proxy)
        else:
            self._client = client

    async def get(
        self,
        url: str,
        *,
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> httpx.Response:
        """Perform an async GET request.

        Note: The proxies parameter is ignored. Configure proxies via __init__.
        """
        return await self._client.get(url, timeout=timeout, headers=headers)

    async def post(
        self,
        url: str,
        *,
        data: dict[str, Any],
        timeout: Optional[float],
        proxies: Optional[dict],
        headers: Optional[dict],
    ) -> httpx.Response:
        """Perform an async POST request.

        Note: The proxies parameter is ignored. Configure proxies via __init__.
        """
        return await self._client.post(url, data=data, timeout=timeout, headers=headers)

    async def aclose(self) -> None:
        """Close the async client and release resources."""
        await self._client.aclose()
