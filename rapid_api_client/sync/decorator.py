"""
Decorator used to build the request and send it with httpx
"""

from functools import partial, wraps
from inspect import signature
from typing import (
    Callable,
    Type,
    overload,
)

from httpx import Client, Response
from pydantic import TypeAdapter

from ..client import BM, RapidApi, RapidParameters, T


@overload
def http(
    method: str,
    path: str,
    response_class: Type[Response] = Response,
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Response]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[str],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., str]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[bytes],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., bytes]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[BM],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., BM]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: TypeAdapter[T],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., T]]: ...


def http(
    method: str,
    path: str,
    response_class: Type[BM | str | bytes | Response] | TypeAdapter[T] = Response,
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., BM | str | bytes | Response | T]]:
    """
    Main decorator used to generate an http request and return its result
    """

    def decorator(
        func: Callable,
    ) -> Callable[..., BM | str | bytes | Response | T]:
        sig = signature(func)
        rapid_parameters = RapidParameters.from_sig(sig)

        @wraps(func)
        def wrapper(api: RapidApi, *args, **kwargs) -> BM | str | bytes | Response | T:
            assert isinstance(api, RapidApi), f"{api} should be an instance of RapidApi"
            assert isinstance(
                api.client, Client
            ), f"{api.client} should be an instance of httpx.Client"

            request = api._build_request(
                sig, rapid_parameters, method, path, (api,) + args, kwargs, timeout
            )
            response = api.client.send(request)
            return api._handle_response(response, response_class=response_class)

        return wrapper

    return decorator


get = partial(http, "GET")
post = partial(http, "POST")
delete = partial(http, "DELETE")
put = partial(http, "PUT")
patch = partial(http, "PATCH")
