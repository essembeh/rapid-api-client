"""
Tests for the @rapid and @rapid_default decorators.
"""

import warnings

from httpx import Client

from rapid_api_client import RapidApi, get, rapid, rapid_default


def test_rapid_default_decorator_base_url():
    """Test that the @rapid_default decorator sets the base_url correctly."""

    @rapid_default(base_url="https://example.com")
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create an instance without specifying base_url
    api = TestApi()

    # Check that the base_url was set correctly
    assert api.client_factory_args["base_url"] == "https://example.com"


def test_rapid_default_decorator_headers():
    """Test that the @rapid_default decorator sets the headers correctly."""

    @rapid_default(headers={"X-Test": "test-value"})
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create an instance without specifying headers
    api = TestApi()

    # Check that the headers were set correctly
    assert api.client_factory_args["headers"]["X-Test"] == "test-value"


def test_rapid_default_decorator_override():
    """Test that instance parameters override decorator parameters."""

    @rapid_default(
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


def test_rapid_default_decorator_with_client():
    """Test that the @rapid_default decorator works with a provided client."""

    @rapid_default(base_url="https://example.com")
    class TestApi(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Create a client
    client = Client(base_url="https://client.com")

    # Create an instance with a provided client
    api = TestApi(client=client)

    # Check that the client was set correctly
    assert api._client is client


def test_rapid_decorator_deprecation_warning():
    """Test that the @rapid decorator raises a deprecation warning."""

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        @rapid(base_url="https://example.com")
        class TestApi(RapidApi):
            @get("/test")
            def test_method(self): ...

        # Check that a deprecation warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "rapid" in str(w[0].message)
        assert "rapid_default" in str(w[0].message)


def test_rapid_decorator_still_works():
    """Test that the deprecated @rapid decorator still works functionally."""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        @rapid(base_url="https://example.com")
        class TestApi(RapidApi):
            @get("/test")
            def test_method(self): ...

        # Create an instance without specifying base_url
        api = TestApi()

        # Check that the base_url was set correctly
        assert api.client_factory_args["base_url"] == "https://example.com"


def test_rapid_and_rapid_default_equivalence():
    """Test that @rapid and @rapid_default produce the same results."""

    # Test with rapid_default
    @rapid_default(base_url="https://example.com", headers={"X-Test": "test"})
    class TestApiDefault(RapidApi):
        @get("/test")
        def test_method(self): ...

    # Test with deprecated rapid (suppress warnings)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)

        @rapid(base_url="https://example.com", headers={"X-Test": "test"})
        class TestApiRapid(RapidApi):
            @get("/test")
            def test_method(self): ...

    # Create instances
    api_default = TestApiDefault()
    api_rapid = TestApiRapid()

    # Check that both behave identically
    assert (
        api_default.client_factory_args["base_url"]
        == api_rapid.client_factory_args["base_url"]
    )
    assert (
        api_default.client_factory_args["headers"]["X-Test"]
        == api_rapid.client_factory_args["headers"]["X-Test"]
    )
