"""
Decorator used to build the request and send it with httpx
"""

import asyncio
from functools import partial, wraps
from inspect import signature
from typing import (
    Any,
    Callable,
    Type,
    overload,
)

from httpx import AsyncClient, Client, Response
from pydantic import TypeAdapter

from .client import BM, RapidApi, RapidParameters, T


@overload
def http(
    method: str,
    path: str,
    response_class: Type[Response] = Response,
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Response]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[str],
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., str]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[bytes],
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., bytes]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[BM],
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., BM]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: TypeAdapter[T],
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., T]]: ...


def http(
    method: str,
    path: str,
    response_class: Type[Response | str | bytes | BM] | TypeAdapter[T] = Response,
    timeout: float | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Response | str | bytes | BM | T]]:
    """
    Main decorator used to generate an http request and return its result
    """

    def decorator(
        func: Callable,
    ) -> Callable[..., Response | str | bytes | BM | T]:
        sig = signature(func)
        rapid_parameters = RapidParameters.from_sig(sig)

        @wraps(func)
        async def awrapper(*args, **kwargs) -> Response | str | bytes | BM | T:
            if not isinstance((api := args[0]), RapidApi):
                raise ValueError(f"{api} should be an instance of RapidApi")
            assert isinstance(
                api.client, AsyncClient
            ), f"{api} should have an async client"

            request = api._build_request(
                sig, rapid_parameters, method, path, args, kwargs, timeout
            )
            response = await api.client.send(request)
            return api._response(response, response_class=response_class)

        @wraps(func)
        def wrapper(*args, **kwargs) -> Response | str | bytes | BM | T:
            if not isinstance((api := args[0]), RapidApi):
                raise ValueError(f"{api} should be an instance of RapidApi")
            assert isinstance(api.client, Client), f"{api} should have a sync client"

            request = api._build_request(
                sig, rapid_parameters, method, path, args, kwargs, timeout
            )
            response = api.client.send(request)
            return api._response(response, response_class=response_class)

        return awrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator


get = partial(http, "GET")
post = partial(http, "POST")
delete = partial(http, "DELETE")
put = partial(http, "PUT")
patch = partial(http, "PATCH")
