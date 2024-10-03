"""
Utility methods
"""

from inspect import Parameter
from typing import Any, Dict, Type, TypeVar, get_args

from rapid_api_client.model import CustomParameter

CP = TypeVar("CP", bound=CustomParameter)


def filter_none_values(values: Dict[str, Any | None]) -> Dict[str, Any]:
    """
    Return a new map with only key/value if the value is set.
    """
    return {k: v for k, v in values.items() if v is not None}


def find_annotation(param: Parameter, cls: Type[CP]) -> CP | None:
    """
    Check if the given parameter has an annotation which is or is a subclass of given type
    """
    if param.annotation:
        for an in get_args(param.annotation):
            if isinstance(an, cls):
                return an
    return None
