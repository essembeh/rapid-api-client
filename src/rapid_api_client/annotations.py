"""
Annotation classes for the rapid-api-client library.

This module provides annotation classes used to customize API requests:
- Path: For URL path parameters
- Query: For URL query parameters
- Header: For HTTP headers
- Body: For request body content
- JsonBody: For JSON request bodies
- FormBody: For form-encoded request bodies
- FileBody: For file uploads
- PydanticBody: For Pydantic models serialized to JSON
- PydanticXmlBody: For Pydantic models serialized to XML

These annotations are used with Python's Annotated type to mark parameters
in API endpoint methods, indicating how they should be processed when
building HTTP requests.

For Pydantic behavior like defaults, validation, or aliases, use a separate
pydantic.Field() annotation alongside the rapid-api-client annotation:

    param: Annotated[str, Query(), Field(default="value", pattern="[a-z]+")]

This dual annotation system provides better separation of concerns and full
compatibility with Pydantic v2's validation system.
"""

from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel

from .xml import pydantic_xml_transformer


@dataclass(slots=True)
class RapidAnnotation:
    """
    Base class for annotations used to customize the request build.

    This class provides a foundation for all request-related annotations in the
    rapid_api_client library. All specific annotation types (Path, Query, Header,
    Body, etc.) inherit from this class.

    For Pydantic behavior like default values, validation, or aliases, use a separate
    pydantic.Field() annotation alongside the rapid-api-client annotation:

        param: Annotated[str, Query(), Field(default="value", pattern="[a-z]+")]

    Attributes:
        alias: Optional alternative name for the parameter when building requests
        transformer: Optional callable that transforms the parameter value before
                    it's used in the request. If None, no transformation is applied.

    Args:
        alias: Optional alternative name for the parameter
        transformer: Optional function to transform the parameter value.
                    Should accept Any and return Any.
    """

    alias: Optional[str] = field(default=None)
    transformer: Optional[Callable[[Any], Any]] = field(default=None)


@dataclass(slots=True)
class Path(RapidAnnotation):
    """
    Annotation to declare an argument used to resolve the API path/URL.

    Use this annotation with the Annotated type to mark parameters that
    should be substituted into the URL path. By default, values are converted
    to strings using the built-in str() function.

    For Pydantic validation or behavior, add a Field() annotation:
        param: Annotated[str, Path(), Field(pattern="[a-z]+")]

    Args:
        alias: Optional alternative name for the path parameter
        transformer: Optional function to transform the parameter value before
                    URL substitution. Defaults to str() for string conversion.

    Example:
        >>> from typing import Annotated, Literal
        >>> from pydantic import Field
        >>> from rapid_api_client import RapidApi, Path, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]): ...
        ...
        ...     # With validation using Field()
        ...     @get("/users/{status}")
        ...     def get_by_status(self, status: Annotated[Literal["active", "inactive"], Path()]): ...
        ...
        ...     # With pattern validation
        ...     @get("/users/{username}")
        ...     def get_by_username(self, username: Annotated[str, Path(), Field(pattern="[a-z]+")]): ...
        ...
        ...     # With custom transformer
        ...     @get("/events/{event_date}")
        ...     def get_events(self, event_date: Annotated[datetime, Path(transformer=lambda x: x.isoformat())]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> user = api.get_user(123)  # Makes request to https://api.example.com/users/123
        >>> events = api.get_events(datetime.now())  # Uses ISO format for date
    """

    def __post_init__(self):
        if self.transformer is None:
            self.transformer = str


@dataclass(slots=True)
class Query(RapidAnnotation):
    """
    Annotation to declare an argument used as a query parameter.

    Use this annotation with the Annotated type to mark parameters that
    should be added to the URL as query parameters. By default, values are
    converted to strings using the built-in str() function.

    For Pydantic behavior like defaults or validation, add a Field() annotation:
        param: Annotated[str, Query(), Field(default="value", max_length=10)]

    Args:
        alias: Optional alternative name for the query parameter
        transformer: Optional function to transform the parameter value before
                    adding to query string. Defaults to str() for string conversion.

    Example:
        >>> from typing import Annotated, Literal
        >>> from pydantic import Field
        >>> from rapid_api_client import RapidApi, Query, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/search")
        ...     def search(
        ...         self,
        ...         q: Annotated[str, Query()],
        ...         page: Annotated[int, Query()] = 1
        ...     ): ...
        ...
        ...     # With Pydantic default value
        ...     @get("/items")
        ...     def get_items(self, limit: Annotated[int, Query(), Field(default=10)]): ...
        ...
        ...     # With validation
        ...     @get("/users")
        ...     def get_users(self, status: Annotated[Literal["active", "inactive"], Query()]): ...
        ...
        ...     # With pattern validation
        ...     @get("/search")
        ...     def search_validated(self, q: Annotated[str, Query(), Field(max_length=100)]): ...
        ...
        ...     # With custom transformer
        ...     @get("/events")
        ...     def get_events(self, date: Annotated[datetime, Query(transformer=lambda x: x.isoformat())]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> results = api.search("python")  # Makes request to https://api.example.com/search?q=python&page=1
        >>> events = api.get_events(datetime.now())  # Uses ISO format for date parameter
    """

    def __post_init__(self):
        if self.transformer is None:
            self.transformer = str


@dataclass(slots=True)
class Header(RapidAnnotation):
    """
    Annotation to declare an argument used as a request header.

    Use this annotation with the Annotated type to mark parameters that
    should be added to the HTTP request headers. By default, values are
    converted to strings using the built-in str() function.

    For Pydantic behavior like validation, add a Field() annotation:
        param: Annotated[str, Header(), Field(pattern="Bearer .+")]

    Args:
        alias: Optional alternative name for the header
        transformer: Optional function to transform the parameter value before
                    adding to headers. Defaults to str() for string conversion.

    Example:
        >>> from typing import Annotated, Literal
        >>> from pydantic import Field
        >>> from rapid_api_client import RapidApi, Header, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/protected")
        ...     def get_protected(self, authorization: Annotated[str, Header()]): ...
        ...
        ...     # With validation
        ...     @get("/api")
        ...     def get_with_validation(self, auth: Annotated[str, Header(), Field(pattern="Bearer .+")]): ...
        ...
        ...     # With literal validation
        ...     @get("/content")
        ...     def get_content(self, accept: Annotated[Literal["application/json", "application/xml"], Header()]): ...
        ...
        ...     # With custom transformer
        ...     @get("/timestamp")
        ...     def get_with_timestamp(self, timestamp: Annotated[datetime, Header(transformer=lambda x: x.isoformat())]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> data = api.get_protected("Bearer token123")  # Adds "Authorization: Bearer token123" header
        >>> data = api.get_with_timestamp(datetime.now())  # Uses ISO format for timestamp header
    """

    def __post_init__(self):
        if self.transformer is None:
            self.transformer = str


@dataclass(slots=True)
class Body(RapidAnnotation):
    """
    Annotation to declare an argument used as HTTP content for POST/PUT/PATCH requests.

    This is the base class for all body-related annotations. It's used to mark
    parameters that should be sent in the request body.

    Example:
        >>> from typing import Annotated
        >>> from rapid_api_client import RapidApi, Body, post
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/data")
        ...     def send_data(self, data: Annotated[str, Body()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> response = api.send_data("raw content")  # Sends "raw content" as the request body
    """

    keyword: Literal["content", "data", "json", "files"] = "content"


@dataclass(slots=True)
class JsonBody(Body):
    """
    Annotation to declare an argument used as JSON object for POST/PUT/PATCH requests.

    Use this annotation to mark dictionary parameters that should be serialized
    to JSON and sent in the request body.

    Example:
        >>> from typing import Annotated, Dict, Any
        >>> from rapid_api_client import RapidApi, JsonBody, post
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/users")
        ...     def create_user(self, user: Annotated[Dict[str, Any], JsonBody()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> response = api.create_user({"name": "John", "email": "john@example.com"})
        >>> # Sends {"name": "John", "email": "john@example.com"} as JSON
    """

    def __post_init__(self):
        self.keyword = "json"


@dataclass(slots=True)
class FormBody(Body):
    """
    Annotation to declare an argument used as URL-encoded form parameter.

    Use this annotation to mark parameters that should be sent as form data
    in the request body.

    Behavior:
    - If the annotated parameter is a Dict[str, str], its content will be merged
      with other form parameters
    - Otherwise, the parameter's name (or alias) and its serialized value will be
      added to the other form parameters

    Example:
        >>> from typing import Annotated, Dict
        >>> from rapid_api_client import RapidApi, FormBody, post
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/login")
        ...     def login(
        ...         self,
        ...         username: Annotated[str, FormBody()],
        ...         password: Annotated[str, FormBody()]
        ...     ): ...
        ...
        ...     @post("/update")
        ...     def update(self, form_data: Annotated[Dict[str, str], FormBody()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> api.login("user123", "pass456")  # Sends username=user123&password=pass456
        >>> api.update({"field1": "value1", "field2": "value2"})  # Sends field1=value1&field2=value2
    """

    def __post_init__(self):
        self.keyword = "data"


@dataclass(slots=True)
class FileBody(Body):
    """
    Annotation to declare an argument used as file to be uploaded.

    Use this annotation to mark parameters that contain file data to be
    uploaded in multipart/form-data requests.

    Example:
        >>> from typing import Annotated, BinaryIO
        >>> from rapid_api_client import RapidApi, FileBody, post
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/upload")
        ...     def upload_file(self, file: Annotated[BinaryIO, FileBody()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> with open("document.pdf", "rb") as f:
        ...     response = api.upload_file(f)  # Uploads document.pdf as multipart/form-data
    """

    def __post_init__(self):
        self.keyword = "files"


@dataclass(slots=True)
class PydanticBody(Body):
    """
    Annotation to declare a Pydantic model to be serialized to JSON and used as HTTP content.

    Use this annotation to mark Pydantic model parameters that should be
    serialized to JSON and sent in the request body. By default, uses Pydantic's
    model_dump_json() with by_alias=True and exclude_none=True.

    Args:
        transformer: Optional function to transform the Pydantic model.
                    Defaults to a function that calls model.model_dump_json(by_alias=True, exclude_none=True).
                    Use functools.partial for custom serialization options.

    Example:
        >>> from typing import Annotated
        >>> from functools import partial
        >>> from pydantic import BaseModel
        >>> from rapid_api_client import RapidApi, PydanticBody, post
        >>>
        >>> class User(BaseModel):
        ...     name: str
        ...     email: str
        ...     age: int
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/users")
        ...     def create_user(self, user: Annotated[User, PydanticBody()]): ...
        ...
        ...     @post("/users/custom")
        ...     def create_user_custom(self, user: Annotated[User, PydanticBody(
        ...         transformer=partial(BaseModel.model_dump_json, exclude_none=False)
        ...     )]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> new_user = User(name="John", email="john@example.com", age=30)
        >>> response = api.create_user(new_user)  # Uses default serialization
        >>> response = api.create_user_custom(new_user)  # Uses custom serialization options
    """

    def __post_init__(self):
        if self.transformer is None:
            self.transformer = partial(
                BaseModel.model_dump_json, by_alias=True, exclude_none=True
            )


@dataclass(slots=True)
class PydanticXmlBody(Body):
    """
    Annotation to declare a Pydantic XML model to be serialized to XML and used as HTTP content.

    Use this annotation to mark Pydantic XML model parameters that should be
    serialized to XML and sent in the request body. Requires the pydantic-xml
    package to be installed. By default, uses BaseXmlModel.to_xml() with exclude_none=True.

    Args:
        transformer: Optional function to transform the Pydantic XML model.
                    Defaults to a function that calls model.to_xml(exclude_none=True).
                    Use functools.partial for custom serialization options.

    Example:
        >>> from typing import Annotated
        >>> from functools import partial
        >>> from pydantic_xml import BaseXmlModel, element
        >>> from rapid_api_client import RapidApi, PydanticXmlBody, post
        >>>
        >>> class User(BaseXmlModel):
        ...     name: str = element()
        ...     email: str = element()
        ...     age: int = element()
        >>>
        >>> class MyApi(RapidApi):
        ...     @post("/users")
        ...     def create_user(self, user: Annotated[User, PydanticXmlBody()]): ...
        ...
        ...     @post("/users/custom")
        ...     def create_user_custom(self, user: Annotated[User, PydanticXmlBody(
        ...         transformer=partial(BaseXmlModel.to_xml, exclude_none=False, skip_empty=False)
        ...     )]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> new_user = User(name="John", email="john@example.com", age=30)
        >>> response = api.create_user(new_user)  # Uses default XML serialization
        >>> response = api.create_user_custom(new_user)  # Uses custom serialization options
    """

    def __post_init__(self):
        if self.transformer is None:
            self.transformer = pydantic_xml_transformer
