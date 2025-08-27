"""
rapid-api-client: A declarative HTTP client library for Python.

This library provides a declarative way to define API clients in Python,
inspired by FastAPI's approach to defining API endpoints. It uses type
annotations and decorators to create clean, type-safe API client interfaces.

Key features:
- Declarative API client definition with decorators
- Type-safe parameter handling with annotations
- Support for path parameters, query parameters, headers, and various body types
- Automatic response conversion based on return type annotations
- Support for both synchronous and asynchronous requests
- Integration with Pydantic for request/response validation and serialization

Basic usage:
    >>> from typing import Annotated
    >>> from rapid_api_client import RapidApi, get, post, Path, JsonBody
    >>>
    >>> class MyApi(RapidApi):
    ...     @get("/users/{user_id}")
    ...     def get_user(self, user_id: Annotated[int, Path()]): ...
    ...
    ...     @post("/users")
    ...     def create_user(self, user: Annotated[dict, JsonBody()]): ...
    >>>
    >>> api = MyApi(base_url="https://api.example.com")
    >>> user = api.get_user(123)
"""

from importlib.metadata import version

from .annotations import (
    Body,
    FileBody,
    FormBody,
    Header,
    JsonBody,
    Path,
    PydanticBody,
    PydanticXmlBody,
    Query,
)
from .client import RapidApi
from .decorator import delete, get, http, patch, post, put, rapid
from .response import ResponseModel

__version__ = version(__name__)
__all__ = [
    "Body",
    "delete",
    "FileBody",
    "FormBody",
    "get",
    "Header",
    "http",
    "JsonBody",
    "patch",
    "Path",
    "post",
    "put",
    "PydanticBody",
    "PydanticXmlBody",
    "Query",
    "rapid",
    "RapidApi",
    "ResponseModel",
]
