# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

from __future__ import annotations

from typing import Any, Optional

import requests


class RequestsTransport:
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
