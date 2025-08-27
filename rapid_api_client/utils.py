"""
Utility functions for the rapid-api-client library.

This module provides utility functions used throughout the library for:
- Processing HTTP responses and converting them to various types
- Finding annotations in function parameters
- Filtering None values from dictionaries

These functions are primarily used internally by the library but may also be
useful for advanced use cases.
"""

from inspect import Parameter
from typing import Any, Dict, Optional, Type, TypeVar, get_args

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
