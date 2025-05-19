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
"""

from pydantic.fields import FieldInfo

from .serializer import (
    ModelSerializer,
    default_pydantic_serializer,
    default_pydanticxml_serializer,
)


class BaseAnnotation(FieldInfo):
    """
    Base class for annotations used to customize the request build.

    This class extends Pydantic's FieldInfo to provide a foundation for
    all request-related annotations in the rapid_api_client library.
    All specific annotation types (Path, Query, Header, Body, etc.) inherit
    from this class.

    Attributes:
        Inherits all attributes from pydantic.fields.FieldInfo, including:
        - default: Default value for the field
        - default_factory: Callable that returns a default value
        - alias: Alternative name for the field
    """


class Path(BaseAnnotation):
    """
    Annotation to declare an argument used to resolve the API path/URL.

    Use this annotation with the Annotated type to mark parameters that
    should be substituted into the URL path.

    Example:
        >>> from typing import Annotated
        >>> from rapid_api_client import RapidApi, Path, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> user = api.get_user(123)  # Makes request to https://api.example.com/users/123
    """


class Query(BaseAnnotation):
    """
    Annotation to declare an argument used as a query parameter.

    Use this annotation with the Annotated type to mark parameters that
    should be added to the URL as query parameters.

    Example:
        >>> from typing import Annotated
        >>> from rapid_api_client import RapidApi, Query, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/search")
        ...     def search(self, q: Annotated[str, Query()], page: Annotated[int, Query()] = 1): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> results = api.search("python")  # Makes request to https://api.example.com/search?q=python&page=1
    """


class Header(BaseAnnotation):
    """
    Annotation to declare an argument used as a request header.

    Use this annotation with the Annotated type to mark parameters that
    should be added to the HTTP request headers.

    Example:
        >>> from typing import Annotated
        >>> from rapid_api_client import RapidApi, Header, get
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/protected")
        ...     def get_protected(self, authorization: Annotated[str, Header()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> data = api.get_protected("Bearer token123")  # Adds "Authorization: Bearer token123" header
    """


class Body(BaseAnnotation):
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


class PydanticBody(Body):
    """
    Annotation to declare a Pydantic model to be serialized to JSON and used as HTTP content.

    Use this annotation to mark Pydantic model parameters that should be
    serialized to JSON and sent in the request body.

    Example:
        >>> from typing import Annotated
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
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> new_user = User(name="John", email="john@example.com", age=30)
        >>> response = api.create_user(new_user)  # Serializes the User model to JSON
    """

    __slots__ = ["model_serializer"]

    def __init__(
        self,
        *args,
        model_serializer: ModelSerializer = default_pydantic_serializer,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model_serializer = model_serializer


class PydanticXmlBody(Body):
    """
    Annotation to declare a Pydantic XML model to be serialized to XML and used as HTTP content.

    Use this annotation to mark Pydantic XML model parameters that should be
    serialized to XML and sent in the request body. Requires the pydantic-xml
    package to be installed.

    Example:
        >>> from typing import Annotated
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
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> new_user = User(name="John", email="john@example.com", age=30)
        >>> response = api.create_user(new_user)  # Serializes the User model to XML
    """

    __slots__ = ["model_serializer"]

    def __init__(
        self,
        *args,
        model_serializer: ModelSerializer = default_pydanticxml_serializer,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model_serializer = model_serializer
