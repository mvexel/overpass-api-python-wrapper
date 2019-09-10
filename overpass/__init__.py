# -*- coding: utf-8 -*-

# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

"""Thin wrapper around the OpenStreetMap Overpass API."""

__title__ = "overpass"
__version__ = "0.6.1"
__license__ = "Apache 2.0"

from .api import API
from .queries import MapQuery, WayQuery
from .errors import (
    OverpassError,
    OverpassSyntaxError,
    TimeoutError,
    MultipleRequestsError,
    ServerLoadError,
    UnknownOverpassError,
)
from .utils import *
