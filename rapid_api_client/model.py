"""
Model classes
"""

from dataclasses import dataclass, field
from typing import Any

from httpx import AsyncClient
from pydantic import BaseModel

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore


@dataclass
class RapidApi:
    """
    Represent an API, a RapidApi subclass should have methods decorated with @http
    which are endpoints
    """

    client: AsyncClient = field(default_factory=AsyncClient)


class CustomParameter:
    """
    Meta class for annotations used to customize the request build
    """


class Path(CustomParameter):
    """
    Annotation to declare an argument used to resolve the api path/url
    """


@dataclass
class Query(CustomParameter):
    """
    Annotation to declare an argument used as a query parameter
    """

    alias: str | None = None


@dataclass
class Header(CustomParameter):
    """
    Annotation to declare an argument used as a request header
    """

    alias: str | None = None


class Body(CustomParameter):
    """
    Annotation to declare an argument used as http content for post/put/...
    """

    def serialize(self, body: Any) -> str | bytes:
        """
        Serialize the annotated parameter value
        """
        return body


@dataclass
class FileBody(Body):
    """
    Annotation to declare an argument used as file to be uploaded
    """

    alias: str | None = None

    def serialize(self, body: Any) -> str | bytes:
        """
        Serialize the annotated parameter value
        """
        return body


@dataclass
class PydanticBody(Body):
    """
    Annotation to declare an argument to be serialized to json and used as http content
    """

    prettyprint: bool = False

    def serialize(self, body: Any) -> str | bytes:
        """
        Serialize the annotated parameter value
        """
        assert isinstance(body, BaseModel)
        return body.model_dump_json(indent=2 if self.prettyprint else None)


@dataclass
class PydanticXmlBody(Body):
    """
    Annotation to declare an argument to be serialized to xml and used as http content
    """

    def serialize(self, body: Any) -> str | bytes:
        """
        Serialize the annotated parameter value
        """
        assert (
            pydantic_xml is not None
        ), "pydantic-xml must be installed to use PydanticXmlBody"
        assert isinstance(body, pydantic_xml.BaseXmlModel)
        return body.to_xml()
