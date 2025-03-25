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

from .annotations import Body as Body
from .annotations import FileBody as FileBody
from .annotations import FormBody as FormBody
from .annotations import Header as Header
from .annotations import JsonBody as JsonBody
from .annotations import Path as Path
from .annotations import PydanticBody as PydanticBody
from .annotations import PydanticXmlBody as PydanticXmlBody
from .annotations import Query as Query
from .client import RapidApi as RapidApi
from .decorator import delete as delete
from .decorator import get as get
from .decorator import http as http
from .decorator import patch as patch
from .decorator import post as post
from .decorator import put as put
from .decorator import rapid as rapid

__version__ = version(__name__)
