"""
Decorator used to build the request and send it with httpx
"""

from functools import partial, wraps
from inspect import signature
from typing import (
    Any,
    Callable,
    Coroutine,
    Type,
    overload,
)

from httpx import Response
from pydantic import TypeAdapter

from .client import BM, CustomParameters, RapidApi, T


@overload
def http(
    method: str,
    path: str,
    response_class: Type[Response] = Response,
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Coroutine[Any, Any, Response]]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[str],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Coroutine[Any, Any, str]]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[bytes],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Coroutine[Any, Any, bytes]]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: Type[BM],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Coroutine[Any, Any, BM]]]: ...


@overload
def http(
    method: str,
    path: str,
    response_class: TypeAdapter[T],
    timeout: float | None = None,
) -> Callable[[Callable], Callable[..., Coroutine[Any, Any, T]]]: ...


def http(
    method: str,
    path: str,
    response_class: Type[BM | str | bytes | Response] | TypeAdapter[T] = Response,
    timeout: float | None = None,
) -> Callable[
    [Callable], Callable[..., Coroutine[Any, Any, BM | str | bytes | Response | T]]
]:
    """
    Main decorator used to generate an http request and return its result
    """

    def decorator(
        func: Callable,
    ) -> Callable[..., Coroutine[Any, Any, BM | str | bytes | Response | T]]:
        sig = signature(func)
        custom_parameters = CustomParameters.from_sig(sig)

        @wraps(func)
        async def wrapper(*args, **kwargs) -> BM | str | bytes | Response | T:
            if not isinstance((api := args[0]), RapidApi):
                raise ValueError(f"{api} should be an instance of RapidApi")
            request = api._build_request(
                sig, custom_parameters, method, path, args, kwargs, timeout
            )
            response = await api.client.send(request)
            return api._handle_response(response, response_class=response_class)

        return wrapper

    return decorator


get = partial(http, "GET")
post = partial(http, "POST")
delete = partial(http, "DELETE")
put = partial(http, "PUT")
patch = partial(http, "PATCH")
