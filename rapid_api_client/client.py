"""
Decorator used to build the httpx request
"""

from dataclasses import dataclass, field
from inspect import Signature
from typing import (
    Any,
    Dict,
    Mapping,
    Self,
    Tuple,
    Type,
    TypeVar,
)

from httpx import AsyncClient, Request, Response
from pydantic import BaseModel, TypeAdapter
from pydantic_xml import BaseXmlModel

from .annotations import BaseAnnotation, Body, FileBody, Header, Path, Query
from .utils import filter_none_values, find_annotation

BM = TypeVar("BM", bound=BaseModel)
T = TypeVar("T")


@dataclass
class CustomParameters:
    """
    Class containing all custom parameters used to build the request.
    """

    path: Dict[str, Path] = field(default_factory=dict)
    query: Dict[str, Query] = field(default_factory=dict)
    headers: Dict[str, Header] = field(default_factory=dict)
    body: Dict[str, Body] = field(default_factory=dict)

    @classmethod
    def from_sig(cls, sig: Signature) -> Self:
        """
        Iterate over parameters of given function to find annotated parameters
        """
        out = cls()
        for parameter in sig.parameters.values():
            annot: BaseAnnotation | None = None
            if (annot := find_annotation(parameter, Path)) is not None:
                out.path[parameter.name] = annot
            if (annot := find_annotation(parameter, Query)) is not None:
                out.query[parameter.name] = annot
            if (annot := find_annotation(parameter, Header)) is not None:
                out.headers[parameter.name] = annot
            if (annot := find_annotation(parameter, Body)) is not None:
                out.body[parameter.name] = annot
        return out


@dataclass
class RapidApi:
    """
    Represent an API, a RapidApi subclass should have methods decorated with @http
    which are endpoints
    """

    client: AsyncClient = field(default_factory=AsyncClient)

    def _build_request(
        self,
        sig: Signature,
        parameters: CustomParameters,
        method: str,
        path: str,
        args: Tuple[Any],
        kwargs: Mapping[str, Any],
        timeout: float | None,
    ) -> Request:
        """
        Build the httpx request with given custom parameters.
        """
        # valuate arguments with default values
        ba = sig.bind(*args, **kwargs)
        ba.apply_defaults()

        # resolve the api path
        path = path.format(**{k: ba.arguments[k] for k in parameters.path})

        build_kwargs: Dict[str, Any] = {}

        build_kwargs["headers"] = filter_none_values(
            {
                annot.alias or param: ba.arguments[param]
                for param, annot in parameters.headers.items()
            }
        )
        build_kwargs["params"] = filter_none_values(
            {
                annot.alias or param: ba.arguments[param]
                for param, annot in parameters.query.items()
            }
        )
        for param, annot in parameters.body.items():
            if (value := ba.arguments[param]) is not None:
                if isinstance(annot, FileBody):
                    files = build_kwargs.setdefault("files", {})
                    files[annot.alias or param] = annot.serialize(value)
                else:
                    build_kwargs[annot.target] = annot.serialize(value)

        # handle extra optional kwargs
        if timeout is not None:
            build_kwargs["timeout"] = timeout

        return self.client.build_request(method, path, **build_kwargs)

    def _handle_response(
        self,
        response: Response,
        response_class: Type[Response | str | bytes | BM] | TypeAdapter[T] = Response,
    ) -> Response | str | bytes | BM | T:
        """
        Parse the response given the expected class
        """
        # do not check response status code if we return the Response itself
        if response_class is Response:
            return response
        # before parsing the response, check its status
        response.raise_for_status()
        if response_class is str:
            return response.text
        if response_class is bytes:
            return response.content
        if isinstance(response_class, TypeAdapter):
            return response_class.validate_json(response.content)
        if issubclass(response_class, BaseXmlModel):
            return response_class.from_xml(response.content)
        if issubclass(response_class, BaseModel):
            return response_class.model_validate_json(response.content)
        raise ValueError(f"Response class not supported: {response_class}")
