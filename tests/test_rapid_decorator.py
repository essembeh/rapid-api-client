"""
Tests for the @rapid decorator.
"""

from httpx import Client

from rapid_api_client import RapidApi, get, rapid


def test_rapid_decorator_base_url():
    """Test that the @rapid decorator sets the base_url correctly."""

    @rapid(base_url="https://example.com")
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create an instance without specifying base_url
    api = TestApi()

    # Check that the base_url was set correctly
    assert api.client_factory_args["base_url"] == "https://example.com"


def test_rapid_decorator_headers():
    """Test that the @rapid decorator sets the headers correctly."""

    @rapid(headers={"X-Test": "test-value"})
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create an instance without specifying headers
    api = TestApi()

    # Check that the headers were set correctly
    assert api.client_factory_args["headers"]["X-Test"] == "test-value"


def test_rapid_decorator_override():
    """Test that instance parameters override decorator parameters."""

    @rapid(
        base_url="https://example.com",
        headers={"X-Test": "test-value", "X-Common": "decorator-value"},
    )
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create an instance with overridden parameters
    api = TestApi(
        base_url="https://override.com",
        headers={"X-Override": "override-value", "X-Common": "instance-value"},
    )

    # Check that the base_url was overridden
    assert api.client_factory_args["base_url"] == "https://override.com"

    # Check that the headers were the user values instead of the decorator values
    assert "X-Test" not in api.client_factory_args["headers"]
    assert api.client_factory_args["headers"]["X-Override"] == "override-value"
    assert api.client_factory_args["headers"]["X-Common"] == "instance-value"


def test_rapid_decorator_with_client():
    """Test that the @rapid decorator works with a provided client."""

    @rapid(base_url="https://example.com")
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create a client
    client = Client(base_url="https://client.com")

    # Create an instance with a provided client
    api = TestApi(client=client)

    # Check that the client was set correctly
    assert api._client is client
