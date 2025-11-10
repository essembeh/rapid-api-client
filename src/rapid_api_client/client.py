"""
Client classes for the rapid-api-client library.

This module provides the core classes for building API clients:
- RapidApi: Base class for API clients
- ParameterManager: Manages parameters for API requests
- RapidParameter: Represents a function parameter with its annotation

These classes handle the extraction of parameters from function signatures,
the resolution of path templates, and the building of HTTP requests.
They work together with the decorator module to provide a declarative way
to define API clients.
"""

from contextlib import asynccontextmanager, contextmanager
from inspect import isclass
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generator,
    Optional,
    Type,
    Union,
    cast,
)

from httpx import AsyncClient, Client, Request, Response
from pydantic import BaseModel, TypeAdapter

from .response import ResponseModel
from .utils import T
from .xml import pydantic_xml


class RapidApi:
    """
    Base class for API clients.

    This class represents an API client. Subclasses should define methods
    decorated with @http (or @get, @post, etc.) which represent API endpoints.

    Example:
        >>> from rapid_api_client import RapidApi, get, post
        >>> from typing import Annotated
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

    def __init__(
        self,
        *,
        client: Client | None = None,
        async_client: AsyncClient | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a RapidApi instance.

        Args:
            client: An existing httpx.Client instance to use for synchronous requests
            async_client: An existing httpx.AsyncClient instance to use for asynchronous requests
            **kwargs: Additional arguments to pass to the httpx.Client and httpx.AsyncClient
                     constructors when creating new clients. Common arguments include:
                     - base_url: The base URL for the API
                     - headers: Default headers to include in all requests
                     - timeout: Default timeout for requests
        """
        self._client: Client | None = client
        self._async_client: AsyncClient | None = async_client
        self.client_factory_args: Dict[str, Any] = kwargs

    @contextmanager
    def sync_client(self) -> Generator[Client, None, None]:
        """
        Context manager that provides access to an httpx.Client instance.

        If a client was provided during initialization, yields that existing client.
        Otherwise, creates a new client using the factory arguments and ensures
        proper cleanup when the context exits.

        Yields:
            Client: An httpx.Client instance for making synchronous HTTP requests

        Example:
            with api.sync_client() as client:
                response = client.get("/endpoint")
        """
        if self._client:
            yield self._client
        else:
            with Client(**self.client_factory_args) as client:
                yield client

    @asynccontextmanager
    async def async_client(self) -> AsyncGenerator[AsyncClient, None]:
        """
        Async context manager that provides access to an httpx.AsyncClient instance.

        If an async client was provided during initialization, yields that existing client.
        Otherwise, creates a new async client using the factory arguments and ensures
        proper cleanup when the context exits.

        Yields:
            AsyncClient: An httpx.AsyncClient instance for making asynchronous HTTP requests

        Example:
            async with api.async_client() as client:
                response = await client.get("/endpoint")
        """
        if self._async_client:
            yield self._async_client
        else:
            async with AsyncClient(**self.client_factory_args) as async_client:
                yield async_client

    def build_request(
        self, client: Union[Client, AsyncClient], *, method: str, url: str, **kwargs
    ) -> Request:
        """
        Build an HTTP request using the provided client.

        This method constructs an httpx.Request object that can be used to make
        HTTP requests. It delegates to the underlying httpx client's build_request
        method while providing a consistent interface for both sync and async clients.

        Args:
            client: The httpx Client or AsyncClient instance to use for building the request
            method: The HTTP method (GET, POST, PUT, DELETE, etc.)
            url: The target URL for the request
            **kwargs: Additional keyword arguments to pass to the client's build_request method.
                     Common arguments include:
                     - params: Query parameters to include in the URL
                     - headers: HTTP headers to include in the request
                     - json: JSON data to send in the request body
                     - data: Form data or raw data to send in the request body
                     - files: Files to upload in the request

        Returns:
            Request: An httpx.Request object ready to be sent

        Example:
            with api.sync_client() as client:
                request = api.build_request(
                    client,
                    method="GET",
                    url="/users/123",
                    params={"include": "profile"}
                )
        """
        return client.build_request(method=method, url=url, **kwargs)

    def process_response(
        self,
        response: Response,
        response_class: Type[T],
        raise_for_status: Optional[bool] = None,
    ) -> T:
        """
        Process an HTTP response and convert it to the specified type.

        This method handles the conversion of raw HTTP responses into typed Python objects.
        It supports various response types including Pydantic models, XML models (via pydantic-xml),
        raw strings, bytes, and httpx.Response objects.

        Args:
            response: The httpx.Response object to process
            response_class: The target type to convert the response to. Supported types include:
                          - httpx.Response: Returns the raw response object
                          - str: Returns the response text content
                          - bytes: Returns the response content as bytes
                          - Pydantic BaseModel subclasses: Parses JSON response into model
                          - pydantic-xml BaseXmlModel subclasses: Parses XML response into model
                          - Other types: Uses TypeAdapter for JSON parsing
            raise_for_status: Whether to raise an exception for HTTP error status codes.
                            - True: Always check status and raise on errors
                            - False: Never check status
                            - None (default): Check status for all types except raw Response

        Returns:
            The processed response converted to the specified type

        Raises:
            HTTPStatusError: When raise_for_status is True and the response has an error status code
            ValidationError: When the response content cannot be parsed into the specified type
            ValueError: When the response format doesn't match the expected type

        Example:
            response = client.get("/users/123")
            user = api.process_response(response, UserModel)

            # For raw response handling
            raw_response = api.process_response(response, Response, raise_for_status=False)
        """
        if response_class is Response:
            # In case of Response, only check status if explicitly asked
            if raise_for_status is True:
                response.raise_for_status()
            return cast(T, response)

        # For other types than Response, check if the response status code indicates an error
        if raise_for_status is not False:
            response.raise_for_status()

        # In case of a string or bytes, return the response content
        if response_class is str:
            return cast(T, response.text)
        if response_class is bytes:
            return cast(T, response.content)

        out: T
        if (
            pydantic_xml is not None
            and isclass(response_class)
            and issubclass(response_class, pydantic_xml.BaseXmlModel)
        ):
            # Check if pydantic-xml is installed and if the response class is a pydantic-xml model
            out = response_class.from_xml(response.content)
        elif isclass(response_class) and issubclass(response_class, BaseModel):
            # Check if the response class is a pydantic model
            out = response_class.model_validate_json(response.content)
        else:
            # Fallback to TypeAdapter for other types
            out = TypeAdapter(response_class).validate_json(response.content)

        # Check if the response class is a subclass of ResponseModel to set the response private attribute
        if isinstance(out, ResponseModel):
            out._response = response
        return cast(T, out)
