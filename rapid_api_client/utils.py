from inspect import Parameter
from typing import Any, Dict, Type, TypeVar, get_args

from rapid_api_client.model import CustomParameter

CP = TypeVar("CP", bound=CustomParameter)


def filter_none_values(values: Dict[str, Any | None]) -> Dict[str, Any]:
    return {k: v for k, v in values.items() if v is not None}


def find_annotation(param: Parameter, cls: Type[CP]) -> CP | None:
    if param.annotation:
        for an in get_args(param.annotation):
            if isinstance(an, cls):
                return an
    return None
