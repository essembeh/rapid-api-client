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
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Generator,
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

    def _request_update(self, request: Request):
        """
        Allow subclasses to update the request id needed. For example to add a signature.

        Args:
            request: the request just before sending to the client
        """
        pass
