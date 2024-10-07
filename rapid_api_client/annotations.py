"""
Model classes
"""

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore


class BaseAnnotation:
    """
    Meta class for annotations used to customize the request build
    """


class Path(BaseAnnotation):
    """
    Annotation to declare an argument used to resolve the api path/url
    """


@dataclass
class Query(BaseAnnotation):
    """
    Annotation to declare an argument used as a query parameter
    """

    alias: str | None = None


@dataclass
class Header(BaseAnnotation):
    """
    Annotation to declare an argument used as a request header
    """

    alias: str | None = None


@dataclass
class Body(BaseAnnotation):
    """
    Annotation to declare an argument used as http content for post/put/...
    """

    target: Literal["content", "data", "files"] = "content"

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

    target: Literal["content", "data", "files"] = "files"
    alias: str | None = None


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
