"""
Utility functions for the rapid-api-client library.

This module provides utility functions used throughout the library for:
- Processing HTTP responses and converting them to various types
- Finding annotations in function parameters
- Filtering None values from dictionaries

These functions are primarily used internally by the library but may also be
useful for advanced use cases.
"""

from inspect import Parameter, isclass
from typing import Any, Dict, Optional, Type, TypeVar, cast, get_args

from httpx import Response
from pydantic import BaseModel, TypeAdapter

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore

from .annotations import BaseAnnotation

T = TypeVar("T")
BA = TypeVar("BA", bound=BaseAnnotation)


def filter_none_values(values: Dict[str, Optional[Any]]) -> Dict[str, Any]:
    """
    Filter out None values from a dictionary.

    This function creates a new dictionary containing only the key-value pairs
    from the input dictionary where the value is not None. This is useful for
    preparing request parameters where None values should be omitted.

    Args:
        values: A dictionary that may contain None values

    Returns:
        A new dictionary with the same keys as the input, but with None values removed

    Examples:
        >>> filter_none_values({"a": 1, "b": None, "c": "value"})
        {"a": 1, "c": "value"}

        >>> filter_none_values({"a": None})
        {}
    """
    return {k: v for k, v in values.items() if v is not None}


def find_annotation(param: Parameter, cls: Type[BA]) -> Optional[BA]:
    """
    Find an annotation of a specific type in a parameter's annotation.

    This function examines a parameter's annotation to find if it contains
    an annotation of the specified type or a subclass of that type. It's used
    to extract specific annotations (like Path, Query, Header, etc.) from
    function parameters.

    Args:
        param: The parameter to check for annotations
        cls: The annotation type to look for

    Returns:
        The found annotation instance if it exists, otherwise None

    Example:
        >>> from inspect import signature
        >>> from typing import Annotated
        >>> from rapid_api_client import Header
        >>>
        >>> def func(x: Annotated[str, Header()]): pass
        >>> param = list(signature(func).parameters.values())[0]
        >>> annotation = find_annotation(param, Header)
        >>> annotation is not None
        True
    """
    if param.annotation:
        for an in get_args(param.annotation):
            if isinstance(an, cls) or issubclass(type(an), cls):
                return an
    return None


def process_response(
    response: Response, response_class: Type[T], raise_for_status: bool = True
) -> T:
    """
    Process the HTTP response and convert it to the specified type.

    This function handles the conversion of HTTP responses to various types based on
    the specified response_class. It's a core utility used by the decorator module
    to process API responses according to the return type annotation of the API method.

    The conversion logic follows these rules:
    1. If response_class is Response, return the raw response object
    2. If response_class is str, return response.text
    3. If response_class is bytes, return response.content
    4. If response_class is a Pydantic XML model, parse the XML content
    5. If response_class is a Pydantic model, parse the JSON content
    6. For any other type, use Pydantic's TypeAdapter to validate the JSON content

    Args:
        response: The HTTP response object from httpx
        response_class: The class to convert the response to (typically from the return
                       type annotation of the API method)
        raise_for_status: Whether to call response.raise_for_status() before processing
                         the response. If True (default), HTTP errors (4xx, 5xx) will
                         raise an HTTPStatusError. Set to False to skip this check.

    Returns:
        The response converted to the specified type

    Raises:
        HTTPStatusError: If raise_for_status is True and the response status code
                        indicates an error (4xx, 5xx)
        ValidationError: If the response content cannot be parsed into the specified type
        TypeError: If the response_class is not supported

    Examples:
        # Return raw Response object
        >>> process_response(response, Response)
        <Response [200 OK]>

        # Convert to string
        >>> process_response(response, str)
        '{"key": "value"}'

        # Convert to bytes
        >>> process_response(response, bytes)
        b'{"key": "value"}'

        # Convert to Pydantic model
        >>> class MyModel(BaseModel):
        ...     key: str
        >>> process_response(response, MyModel)
        MyModel(key='value')

        # Convert to dataclass or other type
        >>> @dataclass
        ... class MyDataClass:
        ...     key: str
        >>> process_response(response, MyDataClass)
        MyDataClass(key='value')

        # Skip HTTP status check
        >>> process_response(response, str, raise_for_status=False)
        '{"error": "Not found"}'
    """
    if response_class is Response:
        return cast(T, response)

    # For other types than Response, check if the response status code indicates an error
    if raise_for_status:
        response.raise_for_status()

    # In case of a string or bytes, return the response content
    if response_class is str:
        return cast(T, response.text)
    if response_class is bytes:
        return cast(T, response.content)

    # Check if pydantic-xml is installed
    if pydantic_xml is not None:
        # Check if the response class is a pydantic-xml model
        if isclass(response_class) and issubclass(
            response_class, pydantic_xml.BaseXmlModel
        ):
            return cast(T, response_class.from_xml(response.content))

    # Check if the response class is a pydantic model
    if isclass(response_class) and issubclass(response_class, BaseModel):
        return cast(T, response_class.model_validate_json(response.content))

    # Fallback to TypeAdapter for other types
    return cast(T, TypeAdapter(response_class).validate_json(response.content))
