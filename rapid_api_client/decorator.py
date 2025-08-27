"""
Decorators for the rapid-api-client library.

This module provides decorators used to mark methods in RapidApi subclasses
as API endpoints:
- http: Main decorator for all HTTP methods
- get: Convenience decorator for GET requests
- post: Convenience decorator for POST requests
- put: Convenience decorator for PUT requests
- patch: Convenience decorator for PATCH requests
- delete: Convenience decorator for DELETE requests

These decorators handle the building of HTTP requests from method signatures,
sending the requests, and processing the responses.
"""

import inspect
from functools import partial, wraps
from inspect import signature
from typing import Any, Dict, Optional, Type

from httpx import Response

from .client import RapidApi
from .parameters import ParameterManager
from .response import process_response


def http(
    method: str,
    path: str,
    timeout: float | None = None,
    headers: Dict[str, str] | None = None,
    raise_for_status: Optional[bool] = None,
    skip_request_update: bool = False,
) -> Any:
    """
    Main decorator used to generate an HTTP request and return its result.

    This decorator is used to mark methods in a RapidApi subclass as API endpoints.
    It works with both synchronous and asynchronous methods, automatically detecting
    which to use based on whether the decorated function is a coroutine function.

    The decorated method's parameters can be annotated with Path, Query, Header,
    or Body annotations to specify how they should be used in the request.
    The method's return annotation is used to determine how to process the response.

    Args:
        method: The HTTP method to use (GET, POST, PUT, DELETE, PATCH, etc.)
        path: The URL path template, which can contain placeholders for path parameters
        timeout: Optional timeout for the request in seconds
        headers: Optional additional headers to include in the request
        raise_for_status: Whether to raise an exception for non-2xx status codes
        skip_request_update: To skip calling RapidApi._request_update before sending

    Returns:
        A decorator function that wraps the API endpoint method

    Example:
        >>> from rapid_api_client import RapidApi, http
        >>> from typing import Annotated
        >>>
        >>> class MyApi(RapidApi):
        ...     @http("GET", "/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]): ...
    """

    def decorator(func):
        sig = signature(func)
        parameter_manager = ParameterManager.from_sig(sig)
        response_class = (
            sig.return_annotation if sig.return_annotation != sig.empty else Response
        )
        is_async = inspect.iscoroutinefunction(func)

        def prepare_request(api: RapidApi, args, kwargs):
            assert isinstance(api, RapidApi), f"{api} should be an instance of RapidApi"

            # valuate arguments from args and kwargs
            # use partial binding not to fail on optional arguments with pydantic default values
            ba = sig.bind_partial(api, *args, **kwargs)
            # apply default values for optional arguments from python signature
            ba.apply_defaults()

            # resolve the api path
            resolved_path = parameter_manager.get_resolved_path(path, ba)

            build_kwargs: Dict[str, Any] = {
                "headers": parameter_manager.get_headers(ba),
                "params": parameter_manager.get_query(ba),
            }
            post_kw, post_data = parameter_manager.get_body(ba)
            if post_kw is not None:
                build_kwargs[post_kw] = post_data
            if timeout is not None:
                build_kwargs["timeout"] = timeout
            if headers is not None:
                for k, v in headers.items():
                    build_kwargs["headers"].setdefault(k, v)

            out = (
                api.async_client.build_request(method, resolved_path, **build_kwargs)
                if is_async
                else api.client.build_request(method, resolved_path, **build_kwargs)
            )
            # call the method allowing the client to update the request before sending it
            if not skip_request_update:
                api._request_update(out)
            return out

        @wraps(func)
        async def async_wrapper(api: RapidApi, *args, **kwargs):
            request = prepare_request(api, args, kwargs)
            response = await api.async_client.send(request)
            return process_response(
                response, response_class, raise_for_status=raise_for_status
            )

        @wraps(func)
        def wrapper(api: RapidApi, *args, **kwargs):
            request = prepare_request(api, args, kwargs)
            response = api.client.send(request)
            return process_response(
                response, response_class, raise_for_status=raise_for_status
            )

        return async_wrapper if is_async else wrapper

    return decorator


def rapid(**default_kwargs: Any) -> Any:
    """
    Class decorator to configure RapidApi subclasses with default parameters.

    This decorator allows specifying default parameters for RapidApi subclasses
    that will be passed to the constructor when instantiating the class.

    Args:
        **kwargs: Default arguments to pass to the RapidApi constructor

    Returns:
        A decorator function that wraps the RapidApi subclass

    Example:
        >>> from rapid_api_client import RapidApi, rapid, get
        >>> from typing import Annotated
        >>>
        >>> @rapid(base_url="https://api.example.com", headers={"X-API-Key": "default-key"})
        >>> class MyApi(RapidApi):
        ...     @get("/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]): ...
        >>>
        >>> # No need to specify base_url or headers, they're provided by the decorator
        >>> api = MyApi()
        >>> user = api.get_user(123)
        >>>
        >>> # You can still override the defaults if needed
        >>> custom_api = MyApi(headers={"X-API-Key": "custom-key"})
    """

    def decorator(cls: Type[RapidApi]) -> Type[RapidApi]:
        # Store the original __init__ method
        original_init = cls.__init__

        @wraps(original_init)
        def __init__(self: RapidApi, **init_kwargs: Any) -> None:
            # Only apply default parameters if not present
            for key, value in default_kwargs.items():
                if key not in init_kwargs:
                    init_kwargs[key] = value
            # Call the original __init__ with the merged kwargs
            original_init(self, **init_kwargs)

        # Replace the __init__ method
        cls.__init__ = __init__  # type: ignore

        return cls

    return decorator


# Convenience decorators for common HTTP methods
get = partial(http, "GET")
post = partial(http, "POST")
delete = partial(http, "DELETE")
put = partial(http, "PUT")
patch = partial(http, "PATCH")
