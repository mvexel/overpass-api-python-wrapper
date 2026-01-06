# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.


class OverpassError(Exception):
    """An error during your request occurred.
    Super class for all Overpass api errors."""

    pass


class OverpassSyntaxError(OverpassError, ValueError):
    """The request contains a syntax error."""

    def __init__(self, request: str) -> None:
        self.request = request
        super().__init__(f"The request contains a syntax error: {request}")

    def __str__(self) -> str:
        return f"The request contains a syntax error: {self.request}"

    def __repr__(self) -> str:
        return f"OverpassSyntaxError(request={self.request!r})"


class TimeoutError(OverpassError):
    """A request timeout occurred."""

    def __init__(self, timeout: int | float) -> None:
        self.timeout = timeout
        super().__init__(f"Query timeout of {timeout} seconds exceeded")

    def __str__(self) -> str:
        return f"Query timeout of {self.timeout} seconds exceeded"

    def __repr__(self) -> str:
        return f"TimeoutError(timeout={self.timeout!r})"


class MultipleRequestsError(OverpassError):
    """You are trying to run multiple requests at the same time."""

    pass


class ServerLoadError(OverpassError):
    """The Overpass server is currently under load and declined the request.
    Try again later or retry with reduced timeout value."""

    def __init__(self, timeout: int | float) -> None:
        self.timeout = timeout
        super().__init__(
            f"Server load error: The Overpass server is currently under load. "
            f"Timeout was {timeout} seconds. Try again later or reduce timeout."
        )

    def __str__(self) -> str:
        return (
            f"Server load error: The Overpass server is currently under load. "
            f"Timeout was {self.timeout} seconds. Try again later or reduce timeout."
        )

    def __repr__(self) -> str:
        return f"ServerLoadError(timeout={self.timeout!r})"


class UnknownOverpassError(OverpassError):
    """An unknown kind of error happened during the request."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"UnknownOverpassError(message={self.message!r})"


class ServerRuntimeError(OverpassError):
    """The Overpass server returned a runtime error"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(f"Server runtime error: {message}")

    def __str__(self) -> str:
        return f"Server runtime error: {self.message}"

    def __repr__(self) -> str:
        return f"ServerRuntimeError(message={self.message!r})"
