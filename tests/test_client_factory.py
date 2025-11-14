"""
Tests for client_factory and async_client_factory parameters in RapidApi.
"""

import asyncio
from unittest.mock import Mock

from httpx import AsyncClient, Client

from rapid_api_client import RapidApi, get


def test_sync_client_factory():
    """Test that client_factory is called when provided for sync clients."""

    # Create a mock factory that returns a real Client
    mock_factory = Mock(return_value=Client(base_url="https://test.com"))

    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create API with custom client factory
    api = TestApi(
        base_url="https://example.com", timeout=30, client_factory=mock_factory
    )

    # Use the sync client context manager
    with api.sync_client() as client:
        # Verify factory was called with the factory args
        mock_factory.assert_called_once_with(base_url="https://example.com", timeout=30)
        # Verify we got a Client instance
        assert isinstance(client, Client)

    # Cleanup the mock return value
    mock_factory.return_value.close()


def test_async_client_factory():
    """Test that async_client_factory is called when provided for async clients."""

    # Create a mock factory that returns a real AsyncClient
    mock_factory = Mock(return_value=AsyncClient(base_url="https://test.com"))

    class TestApi(RapidApi):
        @get("/test")
        async def test_method(self): ...

    # Create API with custom async client factory
    api = TestApi(
        base_url="https://example.com", timeout=30, async_client_factory=mock_factory
    )

    # Use the async client context manager
    async def test_async():
        async with api.async_client() as client:
            # Verify factory was called with the factory args
            mock_factory.assert_called_once_with(
                base_url="https://example.com", timeout=30
            )
            # Verify we got an AsyncClient instance
            assert isinstance(client, AsyncClient)

    asyncio.run(test_async())

    # Cleanup the mock return value
    asyncio.run(mock_factory.return_value.aclose())


def test_default_sync_client_without_factory():
    """Test that default Client constructor is used when no client_factory is provided."""

    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create API without custom client factory
    api = TestApi(base_url="https://example.com", timeout=30)

    # Use the sync client context manager
    with api.sync_client() as client:
        # Verify we got a Client instance with correct base_url
        assert isinstance(client, Client)
        assert str(client.base_url) == "https://example.com"


def test_default_async_client_without_factory():
    """Test that default AsyncClient constructor is used when no async_client_factory is provided."""

    class TestApi(RapidApi):
        @get("/test")
        async def test_method(self): ...

    # Create API without custom async client factory
    api = TestApi(base_url="https://example.com", timeout=30)

    # Use the async client context manager
    async def test_async():
        async with api.async_client() as client:
            # Verify we got an AsyncClient instance with correct base_url
            assert isinstance(client, AsyncClient)
            assert str(client.base_url) == "https://example.com"

    asyncio.run(test_async())


def test_provided_client_overrides_factory():
    """Test that provided client instances override factories."""

    # Create mock factories
    mock_sync_factory = Mock(return_value=Client(base_url="https://factory.com"))
    mock_async_factory = Mock(return_value=AsyncClient(base_url="https://factory.com"))

    # Create actual client instances
    provided_sync_client = Client(base_url="https://provided.com")
    provided_async_client = AsyncClient(base_url="https://provided.com")

    class TestApi(RapidApi):
        @get("/test")
        def test_sync(self): ...

        @get("/test")
        async def test_async(self): ...

    # Create API with both provided clients and factories
    api = TestApi(
        base_url="https://example.com",
        client=provided_sync_client,
        async_client=provided_async_client,
        client_factory=mock_sync_factory,
        async_client_factory=mock_async_factory,
    )

    # Test sync client - should use provided client, not factory
    with api.sync_client() as client:
        assert client is provided_sync_client
        mock_sync_factory.assert_not_called()

    # Test async client - should use provided client, not factory
    async def test_async():
        async with api.async_client() as client:
            assert client is provided_async_client
            mock_async_factory.assert_not_called()

    asyncio.run(test_async())

    # Cleanup
    provided_sync_client.close()
    asyncio.run(provided_async_client.aclose())
    mock_sync_factory.return_value.close()
    asyncio.run(mock_async_factory.return_value.aclose())


def test_client_factory_with_different_args():
    """Test that factories receive the correct arguments."""

    def custom_sync_factory(**kwargs):
        # Verify we got the expected arguments
        assert kwargs["base_url"] == "https://custom.com"
        assert kwargs["timeout"] == 60
        assert kwargs["headers"]["X-Custom"] == "test"
        return Client(**kwargs)

    def custom_async_factory(**kwargs):
        # Verify we got the expected arguments
        assert kwargs["base_url"] == "https://custom.com"
        assert kwargs["timeout"] == 60
        assert kwargs["headers"]["X-Custom"] == "test"
        return AsyncClient(**kwargs)

    class TestApi(RapidApi):
        @get("/test")
        def test_sync(self): ...

        @get("/test")
        async def test_async(self): ...

    # Create API with custom arguments
    api = TestApi(
        base_url="https://custom.com",
        timeout=60,
        headers={"X-Custom": "test"},
        client_factory=custom_sync_factory,
        async_client_factory=custom_async_factory,
    )

    # Test sync factory
    with api.sync_client() as client:
        assert isinstance(client, Client)

    # Test async factory
    async def test_async():
        async with api.async_client() as client:
            assert isinstance(client, AsyncClient)

    asyncio.run(test_async())


def test_factory_type_annotations():
    """Test that factory parameters have correct type annotations."""

    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # This should not raise type errors if type checking is enabled
    api = TestApi(
        client_factory=lambda **kwargs: Client(**kwargs),
        async_client_factory=lambda **kwargs: AsyncClient(**kwargs),
    )

    assert api._client_factory is not None
    assert api._async_client_factory is not None
