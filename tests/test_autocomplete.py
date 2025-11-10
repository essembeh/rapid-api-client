"""
Tests for auto-completion and type hinting improvements.

This test verifies that the type annotations on decorated methods
are preserved correctly for IDE auto-completion support.
"""

import inspect
from typing import Annotated, List, get_type_hints

from pydantic import BaseModel

from rapid_api_client import JsonBody, Path, Query, RapidApi, get, post


class User(BaseModel):
    id: int
    name: str
    email: str


class CreateUserRequest(BaseModel):
    name: str
    email: str


class UserApiForTesting(RapidApi):
    """Test API client for auto-completion testing."""

    @get("/users/{user_id}")
    def get_user(self, user_id: Annotated[int, Path()]) -> User:
        """Get a user by ID"""
        ...

    @get("/users")
    def list_users(
        self, page: Annotated[int, Query()] = 1, limit: Annotated[int, Query()] = 10
    ) -> List[User]:
        """List users with pagination"""
        ...

    @post("/users")
    def create_user(self, user: Annotated[CreateUserRequest, JsonBody()]) -> User:
        """Create a new user"""
        ...

    @get("/users/search")
    async def search_users(self, query: Annotated[str, Query()]) -> List[User]:
        """Search users asynchronously"""
        ...


def test_decorator_preserves_function_signature():
    """Test that decorators preserve the original function signature."""
    # Test sync method signature
    get_user_sig = inspect.signature(UserApiForTesting.get_user)
    assert "user_id" in get_user_sig.parameters
    assert get_user_sig.parameters["user_id"].annotation != inspect.Parameter.empty

    # Test method with multiple parameters
    list_users_sig = inspect.signature(UserApiForTesting.list_users)
    assert "page" in list_users_sig.parameters
    assert "limit" in list_users_sig.parameters
    assert list_users_sig.parameters["page"].default == 1
    assert list_users_sig.parameters["limit"].default == 10

    # Test async method signature
    search_users_sig = inspect.signature(UserApiForTesting.search_users)
    assert "query" in search_users_sig.parameters
    assert search_users_sig.parameters["query"].annotation != inspect.Parameter.empty


def test_decorator_preserves_return_annotations():
    """Test that decorators preserve return type annotations for IDE support."""
    # Test return annotations are preserved
    assert UserApiForTesting.get_user.__annotations__.get("return") == User
    assert UserApiForTesting.list_users.__annotations__.get("return") == List[User]
    assert UserApiForTesting.create_user.__annotations__.get("return") == User
    assert UserApiForTesting.search_users.__annotations__.get("return") == List[User]


def test_decorator_preserves_docstrings():
    """Test that decorators preserve method docstrings."""
    assert UserApiForTesting.get_user.__doc__ == "Get a user by ID"
    assert UserApiForTesting.list_users.__doc__ == "List users with pagination"
    assert UserApiForTesting.create_user.__doc__ == "Create a new user"
    assert UserApiForTesting.search_users.__doc__ == "Search users asynchronously"


def test_decorator_preserves_function_name():
    """Test that decorators preserve the original function names."""
    assert UserApiForTesting.get_user.__name__ == "get_user"
    assert UserApiForTesting.list_users.__name__ == "list_users"
    assert UserApiForTesting.create_user.__name__ == "create_user"
    assert UserApiForTesting.search_users.__name__ == "search_users"


def test_async_method_detection():
    """Test that async methods are properly detected and handled."""
    # Sync methods should not be coroutine functions
    assert not inspect.iscoroutinefunction(UserApiForTesting.get_user)
    assert not inspect.iscoroutinefunction(UserApiForTesting.list_users)
    assert not inspect.iscoroutinefunction(UserApiForTesting.create_user)

    # Async methods should be coroutine functions
    assert inspect.iscoroutinefunction(UserApiForTesting.search_users)


def test_type_hints_accessible():
    """Test that type hints are accessible for IDE auto-completion."""
    # Test that get_type_hints works on decorated methods
    get_user_hints = get_type_hints(UserApiForTesting.get_user)
    assert get_user_hints.get("return") == User

    list_users_hints = get_type_hints(UserApiForTesting.list_users)
    assert list_users_hints.get("return") == List[User]

    search_users_hints = get_type_hints(UserApiForTesting.search_users)
    assert search_users_hints.get("return") == List[User]


def test_method_callable_with_correct_signature():
    """Test that decorated methods are callable with the expected signature."""
    # Test the signature inspection directly rather than calling the method
    # since we don't want to make actual HTTP calls in this test

    get_user_sig = inspect.signature(UserApiForTesting.get_user)

    # Test binding arguments to signature
    # Should work with correct parameters
    bound_args = get_user_sig.bind_partial(None, 123)  # None for 'self'
    assert bound_args.arguments["user_id"] == 123

    # Test with keyword arguments
    bound_args_kw = get_user_sig.bind_partial(None, user_id=456)
    assert bound_args_kw.arguments["user_id"] == 456

    # Test list_users with defaults
    list_users_sig = inspect.signature(UserApiForTesting.list_users)
    bound_with_defaults = list_users_sig.bind_partial(None)  # Only 'self'
    bound_with_defaults.apply_defaults()
    assert bound_with_defaults.arguments["page"] == 1
    assert bound_with_defaults.arguments["limit"] == 10

    # Test with custom values
    bound_custom = list_users_sig.bind_partial(None, page=2, limit=20)
    assert bound_custom.arguments["page"] == 2
    assert bound_custom.arguments["limit"] == 20


def test_parameter_annotations_preserved():
    """Test that parameter annotations are preserved for validation."""
    # Check that annotations include the Path/Query/Body information
    get_user_sig = inspect.signature(UserApiForTesting.get_user)
    user_id_annotation = get_user_sig.parameters["user_id"].annotation

    # The annotation should be Annotated[int, Path()]
    assert hasattr(user_id_annotation, "__origin__")  # It's an Annotated type
    assert hasattr(user_id_annotation, "__args__")  # It has arguments

    list_users_sig = inspect.signature(UserApiForTesting.list_users)
    page_annotation = list_users_sig.parameters["page"].annotation
    limit_annotation = list_users_sig.parameters["limit"].annotation

    # Both should be Annotated types with Query
    assert hasattr(page_annotation, "__origin__")
    assert hasattr(limit_annotation, "__origin__")


def test_wrapper_function_properties():
    """Test that wrapper functions maintain expected properties."""
    # Test that the wrapped functions have the correct module
    assert UserApiForTesting.get_user.__module__ == __name__

    # Test that the wrapped functions are bound methods when accessed from instance
    api = UserApiForTesting(base_url="https://example.com")
    assert hasattr(api.get_user, "__self__")  # Bound method
    assert api.get_user.__self__ is api


def test_convenience_decorators_signature_sync():
    """Test that convenience decorators have signatures synchronized with http()."""
    from rapid_api_client.decorator import delete, get, http, patch, post, put

    # Get the signature of http() without the 'method' parameter
    http_sig = inspect.signature(http)
    http_params = list(http_sig.parameters.values())[1:]  # Skip 'method'
    expected_sig = http_sig.replace(parameters=http_params)

    # Test that all convenience decorators have the same signature
    convenience_decorators = [get, post, put, patch, delete]

    for decorator in convenience_decorators:
        decorator_sig = inspect.signature(decorator)

        # Compare parameter names and types
        assert len(decorator_sig.parameters) == len(expected_sig.parameters)

        for (expected_name, expected_param), (actual_name, actual_param) in zip(
            expected_sig.parameters.items(), decorator_sig.parameters.items()
        ):
            assert expected_name == actual_name
            assert expected_param.annotation == actual_param.annotation
            assert expected_param.default == actual_param.default
            assert expected_param.kind == actual_param.kind

        # Test return annotation
        assert decorator_sig.return_annotation == expected_sig.return_annotation
