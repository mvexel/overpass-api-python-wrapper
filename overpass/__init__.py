from importlib.metadata import version

__title__ = "overpass"
__version__ = version("overpass")
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
