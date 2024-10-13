"""
Decorator used to build the httpx request
"""

from dataclasses import dataclass, field
from inspect import BoundArguments, Parameter, Signature
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Mapping,
    Self,
    Tuple,
    Type,
    TypeVar,
)

from httpx import AsyncClient, Request, Response
from pydantic import BaseModel, TypeAdapter
from pydantic_core import PydanticUndefined

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore

from .annotations import (
    BaseAnnotation,
    Body,
    FileBody,
    FormBody,
    Header,
    Path,
    PydanticBody,
    PydanticXmlBody,
    Query,
)
from .utils import filter_none_values, find_annotation

BM = TypeVar("BM", bound=BaseModel)
T = TypeVar("T")
BA = TypeVar("BA", bound=BaseAnnotation)


@dataclass
class RapidParameter(Generic[BA]):
    param: Parameter
    annot: BA

    @property
    def name(self) -> str:
        return self.param.name

    def get_name(self, use_alias: bool = True) -> str:
        if use_alias and self.annot.alias:
            return self.annot.alias
        return self.name

    def get_value(self, ba: BoundArguments, *, validate: bool = True) -> Any:
        out = ba.arguments.get(self.name)
        if out is None:
            # check if pydantic model has a default value or a default factory
            if self.annot.default is not PydanticUndefined:
                out = self.annot.default
            elif self.annot.default_factory is not None:
                out = self.annot.default_factory()
            else:
                # No default value, raise an error
                raise ValueError(f"Missing value for parameter {self.name}")

        if validate:
            out = TypeAdapter(self.param.annotation).validate_python(out)

        return out


@dataclass
class RapidParameters:
    """
    Class containing all custom parameters used to build the request.
    """

    path_parameters: List[RapidParameter[Path]] = field(default_factory=list)
    query_parameters: List[RapidParameter[Query]] = field(default_factory=list)
    header_parameters: List[RapidParameter[Header]] = field(default_factory=list)
    body_parameters: List[RapidParameter[Body]] = field(default_factory=list)

    @classmethod
    def from_sig(cls, sig: Signature) -> Self:
        """
        Iterate over parameters of given function to find annotated parameters
        """
        out = cls()
        for parameter in sig.parameters.values():
            annot: BaseAnnotation | None = None
            if (annot := find_annotation(parameter, Path)) is not None:
                out.path_parameters.append(RapidParameter(parameter, annot))
            if (annot := find_annotation(parameter, Query)) is not None:
                out.query_parameters.append(RapidParameter(parameter, annot))
            if (annot := find_annotation(parameter, Header)) is not None:
                out.header_parameters.append(RapidParameter(parameter, annot))
            if (annot := find_annotation(parameter, Body)) is not None:
                out.body_parameters.append(RapidParameter(parameter, annot))
        return out

    def get_resolved_path(self, path: str, ba: BoundArguments) -> str:
        path_params = filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.path_parameters}
        )
        return path.format(**path_params)

    def get_headers(self, ba: BoundArguments) -> Dict[str, Any]:
        return filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.header_parameters}
        )

    def get_query(self, ba: BoundArguments) -> Dict[str, Any]:
        return filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.query_parameters}
        )


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
        rapid_parameters: RapidParameters,
        method: str,
        path: str,
        args: Tuple[Any],
        kwargs: Mapping[str, Any],
        timeout: float | None,
    ) -> Request:
        """
        Build the httpx request with given custom parameters.
        """
        # valuate arguments from args and kwargs
        # use partial binding not to fail on optional arguments with pydantic default values
        ba = sig.bind_partial(*args, **kwargs)
        # apply default values for optional arguments from python signature
        ba.apply_defaults()

        # resolve the api path
        path = rapid_parameters.get_resolved_path(path, ba)

        build_kwargs: Dict[str, Any] = {
            "headers": rapid_parameters.get_headers(ba),
            "params": rapid_parameters.get_query(ba),
        }
        for rparam in rapid_parameters.body_parameters:
            if (value := rparam.get_value(ba)) is not None:
                if isinstance(rparam.annot, FileBody):
                    files = build_kwargs.setdefault("files", {})
                    files[rparam.get_name()] = value
                elif isinstance(rparam.annot, FormBody):
                    data = build_kwargs.setdefault("data", {})
                    if isinstance(value, dict):
                        data.update(value)
                    else:
                        data[rparam.get_name()] = value
                elif isinstance(rparam.annot, PydanticBody):
                    assert isinstance(value, BaseModel)
                    build_kwargs["content"] = value.model_dump_json()
                elif isinstance(rparam.annot, PydanticXmlBody):
                    assert (
                        pydantic_xml is not None
                    ), "pydantic-xml must be installed to use PydanticXmlBody"
                    assert isinstance(value, pydantic_xml.BaseXmlModel)
                    build_kwargs["content"] = value.to_xml()
                else:
                    build_kwargs["content"] = value

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
        if pydantic_xml is not None and issubclass(
            response_class, pydantic_xml.BaseXmlModel
        ):
            return response_class.from_xml(response.content)
        if issubclass(response_class, BaseModel):
            return response_class.model_validate_json(response.content)
        raise ValueError(f"Response class not supported: {response_class}")
