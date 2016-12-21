# -*- coding: utf-8 -*-

"""Thin wrapper around the OpenStreetMap Overpass API."""

__title__ = 'overpass'
__version__ = '0.1.0'
__license__ = 'Apache 2.0'

from .api import API
from .queries import MapQuery, WayQuery
from .errors import (
    OverpassError, OverpassSyntaxError, TimeoutError, MultipleRequestsError, ServerLoadError, UnknownOverpassError
)
from .utils import *