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

from typing import (
    Any,
    Dict,
)

from httpx import AsyncClient, Client, Request


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

    @property
    def client(self) -> Client:
        """
        Get the synchronous HTTP client.

        If no client was provided in the constructor, a new one is created
        using the arguments provided in the constructor.

        Returns:
            The httpx.Client instance for making synchronous requests
        """
        if self._client is None:
            self._client = Client(**self.client_factory_args)
        return self._client

    @property
    def async_client(self) -> AsyncClient:
        """
        Get the asynchronous HTTP client.

        If no async client was provided in the constructor, a new one is created
        using the arguments provided in the constructor.

        Returns:
            The httpx.AsyncClient instance for making asynchronous requests
        """
        if self._async_client is None:
            self._async_client = AsyncClient(**self.client_factory_args)
        return self._async_client

    def _request_update(self, request: Request):
        """
        Allow subclasses to update the request id needed. For example to add a signature.

        Args:
            request: the request just before sending to the client
        """
        pass
