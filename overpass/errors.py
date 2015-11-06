class OverpassError(Exception):
    """An error during your request occurred.
    Super class for all Overpass api errors."""
    pass


class OverpassSyntaxError(OverpassError, ValueError):
    """The request contains a syntax error."""

    def __init__(self, request):
        self.request = request


class TimeoutError(OverpassError):
    """A request timeout occurred."""

    def __init__(self, timeout):
        self.timeout = timeout


class MultipleRequestsError(OverpassError):
    """You are trying to run multiple requests at the same time."""
    pass


class ServerLoadError(OverpassError):
    """The Overpass server is currently under load and declined the request.
    Try again later or retry with reduced timeout value."""

    def __init__(self, timeout):
        self.timeout = timeout


class UnknownOverpassError(OverpassError):
    """An unknown kind of error happened during the request."""

    def __init__(self, message):
        self.message = message