"""
Serialization utilities for the rapid-api-client library.

This module provides serializer functions that convert Pydantic models to string or binary
representations for use in HTTP requests. It includes:

- ModelSerializer: Type definition for serializer functions
- pydantic_serializer: Creates a serializer for standard Pydantic models (JSON output)
- pydanticxml_serializer: Creates a serializer for Pydantic XML models (XML output)
- Default serializer instances for both formats

These serializers are primarily used with PydanticBody and PydanticXmlBody annotations
to control how Pydantic models are serialized when sent in HTTP request bodies.
"""

from typing import Callable, Union

from pydantic import BaseModel

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore


# Type definition for serializer functions that convert Pydantic models to string or bytes
ModelSerializer = Callable[[BaseModel], Union[str, bytes]]


def pydantic_serializer(**kwargs) -> ModelSerializer:
    """
    Create a serializer function for Pydantic models that outputs JSON.

    This function returns a callable that converts a Pydantic model to a JSON string
    using the model's model_dump_json method. The returned serializer can be used
    with PydanticBody annotations to customize how models are serialized.

    Args:
        **kwargs: Keyword arguments passed to BaseModel.model_dump_json.
            Common options include:
            - exclude_unset (bool): Whether to exclude unset fields
            - exclude_defaults (bool): Whether to exclude fields with default values
            - exclude_none (bool): Whether to exclude fields with None values
            - by_alias (bool): Whether to use field aliases instead of attribute names
            - indent (int): Number of spaces for indentation (None for compact JSON)

    Returns:
        ModelSerializer: A function that takes a BaseModel instance and returns a JSON string

    Example:
        >>> from pydantic import BaseModel
        >>> from rapid_api_client.serializer import pydantic_serializer
        >>>
        >>> class User(BaseModel):
        >>>     name: str
        >>>     age: int = 0
        >>>
        >>> user = User(name="John")
        >>> serializer = pydantic_serializer(exclude_defaults=True)
        >>> serializer(user)  # Returns '{"name":"John"}' (without the age field)
    """

    def out(model: BaseModel) -> str | bytes:
        assert isinstance(model, BaseModel)
        return model.model_dump_json(**kwargs)

    return out


def pydanticxml_serializer(**kwargs) -> ModelSerializer:
    """
    Create a serializer function for Pydantic XML models that outputs XML.

    This function returns a callable that converts a Pydantic XML model to an XML string
    using the model's to_xml method. The returned serializer can be used with
    PydanticXmlBody annotations to customize how models are serialized.

    Note:
        Requires the pydantic-xml package to be installed.

    Args:
        **kwargs: Keyword arguments passed to BaseXmlModel.to_xml.
            Common options include:
            - exclude_unset (bool): Whether to exclude unset fields
            - exclude_defaults (bool): Whether to exclude fields with default values
            - exclude_none (bool): Whether to exclude fields with None values
            - pretty_print (bool): Whether to format the XML with indentation
            - encoding (str): Character encoding for the XML output

    Returns:
        ModelSerializer: A function that takes a BaseXmlModel instance and returns an XML string

    Raises:
        AssertionError: If pydantic-xml is not installed or if the model is not a BaseXmlModel

    Example:
        >>> from pydantic_xml import BaseXmlModel, element
        >>> from rapid_api_client.serializer import pydanticxml_serializer
        >>>
        >>> class User(BaseXmlModel):
        >>>     name: str = element()
        >>>     age: int = element()
        >>>
        >>> user = User(name="John", age=30)
        >>> serializer = pydanticxml_serializer(pretty_print=True)
        >>> serializer(user)  # Returns formatted XML string
    """

    def out(model: BaseModel) -> str | bytes:
        assert pydantic_xml, "pydantic-xml must be installed to use XML serialization"
        assert isinstance(model, pydantic_xml.BaseXmlModel)
        return model.to_xml(**kwargs)

    return out


# Default serializer for Pydantic models (JSON)
# Uses by_alias=True to respect field aliases in the output
default_pydantic_serializer = pydantic_serializer(by_alias=True)

# Default serializer for Pydantic XML models
# Uses exclude_unset=True to omit fields that weren't explicitly set
default_pydanticxml_serializer = pydanticxml_serializer(exclude_unset=True)
