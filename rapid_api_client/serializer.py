"""
Serialization functions for the rapid-api-client library.

This module serializers to convert Pydantic model to str or bytes
"""

from typing import Callable, Union

from pydantic import BaseModel

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore


ModelSerializer = Callable[[BaseModel], Union[str, bytes]]


def pydantic_serializer(model: BaseModel) -> str | bytes:
    """
    Serialize a Pydantic model to JSON.

    This function converts a Pydantic model to its JSON representation,
    respecting field aliases defined in the model.

    Args:
        model: The Pydantic model to serialize

    Returns:
        The JSON representation of the model as a string

    Raises:
        AssertionError: If the provided object is not a Pydantic BaseModel

    Examples:
        >>> from pydantic import BaseModel, Field
        >>> class User(BaseModel):
        ...     user_id: int = Field(alias="id")
        ...     name: str
        >>> user = User(id=1, name="John")
        >>> pydantic_serialize(user)
        '{"id":1,"name":"John"}'
    """
    assert isinstance(model, BaseModel)
    return model.model_dump_json(by_alias=True)


def pydanticxml_serializer(model: BaseModel) -> str | bytes:
    """
    Serialize a Pydantic XML model to XML.

    This function converts a Pydantic XML model to its XML representation,
    excluding unset fields, empty values, and None values.

    Args:
        model: The Pydantic XML model to serialize

    Returns:
        The XML representation of the model as a string or bytes

    Raises:
        AssertionError: If pydantic-xml is not installed or if the provided
                       object is not a pydantic_xml.BaseXmlModel

    Examples:
        >>> from pydantic_xml import BaseXmlModel, element
        >>> class Person(BaseXmlModel):
        ...     name: str = element()
        ...     age: int = element()
        >>> person = Person(name="John", age=30)
        >>> xml_str = pydanticxml_serialize(person)
        >>> print(xml_str)
        <?xml version='1.0' encoding='utf-8'?>
        <Person>
          <name>John</name>
          <age>30</age>
        </Person>
    """
    assert pydantic_xml, "pydantic-xml must be installed to use XML serialization"
    assert isinstance(model, pydantic_xml.BaseXmlModel)
    return model.to_xml(exclude_unset=True, skip_empty=True, exclude_none=True)
