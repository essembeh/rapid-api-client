"""
Client classes for the rapid-api-client library.

This module provides the core classes for building API clients:
- RapidApi: Base class for API clients
- ParameterManager: Manages parameters for API requests
- RapidParameter: Represents a function parameter with its annotation

These classes handle the extraction of parameters from function signatures,
the resolution of path templates, and the building of HTTP requests.
They work together with the decorator module to provide a declarative way
to define API clients.
"""

from dataclasses import dataclass, field
from inspect import BoundArguments, Parameter, Signature
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Self,
    Tuple,
)

from httpx import AsyncClient, Client
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
    JsonBody,
    Path,
    PydanticBody,
    PydanticXmlBody,
    Query,
)
from .utils import BA, filter_none_values, find_annotation


@dataclass
class RapidParameter(Generic[BA]):
    """
    Represents a function parameter with its associated annotation.

    This class is used internally to handle parameters that have been annotated
    with one of the annotation types (Path, Query, Header, Body, etc.).

    Attributes:
        param: The function parameter
        annot: The annotation associated with the parameter
    """

    param: Parameter
    annot: BA

    @property
    def name(self) -> str:
        """
        Get the original parameter name.

        Returns:
            The name of the parameter as defined in the function signature
        """
        return self.param.name

    def get_name(self, use_alias: bool = True) -> str:
        """
        Get the parameter name, using the alias if available and requested.

        Args:
            use_alias: Whether to use the alias defined in the annotation if available

        Returns:
            The parameter name or its alias
        """
        if use_alias and self.annot.alias:
            return self.annot.alias
        return self.name

    def get_value(self, ba: BoundArguments, *, validate: bool = True) -> Any:
        """
        Get the parameter value from bound arguments.

        This method retrieves the parameter value from the bound arguments,
        or uses the default value if the parameter is not in the arguments.
        It can also validate the value against the parameter's type annotation.

        Args:
            ba: The bound arguments from the function call
            validate: Whether to validate the value against the parameter's type annotation

        Returns:
            The parameter value

        Raises:
            ValueError: If the parameter has no value and no default
        """
        out = None
        if self.name in ba.arguments:
            out = ba.arguments.get(self.name)
        else:
            # Use pydantic default value if available
            out = self.annot.get_default(call_default_factory=True)
            if out is PydanticUndefined:
                raise ValueError(f"Missing value for parameter {self.name}")

        if validate:
            out = TypeAdapter(self.param.annotation).validate_python(out)

        return out


@dataclass
class ParameterManager:
    """
    Class containing all custom parameters used to build the request.

    This class manages the different types of parameters (path, query, header, body)
    that are used to build an HTTP request. It extracts these parameters from
    function signatures and provides methods to resolve them into request components.

    Attributes:
        path_parameters: Parameters used to resolve the URL path
        query_parameters: Parameters used as query parameters
        header_parameters: Parameters used as HTTP headers
        body_parameters: Parameters used in the request body
    """

    path_parameters: List[RapidParameter[Path]] = field(default_factory=list)
    query_parameters: List[RapidParameter[Query]] = field(default_factory=list)
    header_parameters: List[RapidParameter[Header]] = field(default_factory=list)
    body_parameters: List[RapidParameter[Body]] = field(default_factory=list)

    @classmethod
    def from_sig(cls, sig: Signature) -> Self:
        """
        Create a ParameterManager from a function signature.

        This method iterates over the parameters of the given function signature
        to find parameters annotated with Path, Query, Header, or Body annotations.
        It also performs consistency checks on body parameters.

        Args:
            sig: The function signature to analyze

        Returns:
            A new ParameterManager instance with the extracted parameters

        Raises:
            AssertionError: If body parameters are inconsistent (e.g., mixing FileBody and FormBody)
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

        # consistency check for body parameters
        if len(out.body_parameters) > 0:
            first_body_param = out.body_parameters[0]
            if isinstance(first_body_param.annot, FileBody):
                # FileBody: check 1+ parameters of type FileBody
                assert all(
                    map(lambda p: isinstance(p.annot, FileBody), out.body_parameters)
                ), "All body parameters must be of type FileBody"
            elif isinstance(first_body_param.annot, FormBody):
                # FormBody: check 1+ parameters of type FormBody
                assert all(
                    map(lambda p: isinstance(p.annot, FormBody), out.body_parameters)
                ), "All body parameters must be of type FormBody"
            elif isinstance(first_body_param.annot, JsonBody):
                # JsonBody: check 1 parameter of type JsonBody
                assert len(out.body_parameters) == 1, "Only one JsonBody allowed"
            elif isinstance(first_body_param.annot, Body):
                # Body: check 1 parameter of type Body
                assert len(out.body_parameters) == 1, "Only one Body allowed"

        return out

    def get_resolved_path(self, path: str, ba: BoundArguments) -> str:
        """
        Resolve the URL path by substituting path parameters.

        Args:
            path: The URL path template with placeholders
            ba: The bound arguments from the function call

        Returns:
            The resolved URL path with parameter values substituted
        """
        path_params = filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.path_parameters}
        )
        return path.format(**path_params)

    def get_headers(self, ba: BoundArguments) -> Dict[str, Any]:
        """
        Get the HTTP headers from header parameters.

        Args:
            ba: The bound arguments from the function call

        Returns:
            A dictionary of HTTP headers
        """
        return filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.header_parameters}
        )

    def get_query(self, ba: BoundArguments) -> Dict[str, Any]:
        """
        Get the query parameters.

        Args:
            ba: The bound arguments from the function call

        Returns:
            A dictionary of query parameters
        """
        return filter_none_values(
            {p.get_name(): p.get_value(ba) for p in self.query_parameters}
        )

    def get_body(self, ba: BoundArguments) -> Tuple[str | None, Any]:
        """
        Get the request body and its type.

        This method processes body parameters based on their annotation type
        (FileBody, FormBody, PydanticXmlBody, PydanticBody, JsonBody, or Body)
        and returns the appropriate body content and type.

        Args:
            ba: The bound arguments from the function call

        Returns:
            A tuple containing the body type (files, data, content, json, or None)
            and the body content

        Raises:
            AssertionError: If using PydanticXmlBody without pydantic-xml installed
                           or if a value doesn't match its expected type
        """
        # check if no body parameters defined
        if len(self.body_parameters) > 0:
            first_body_param = self.body_parameters[0]

            if isinstance(first_body_param.annot, FileBody):
                # there are one or more files
                values = filter_none_values(
                    {p.get_name(): p.get_value(ba) for p in self.body_parameters}
                )
                if len(values) > 0:
                    return "files", values
            elif isinstance(first_body_param.annot, FormBody):
                # there are one or more form parameters
                values = {}

                def update_values(p: RapidParameter[Body]) -> None:
                    # FormBody parameters can be a dict or a single value
                    if (value := p.get_value(ba)) is not None:
                        if isinstance(value, dict):
                            # for dict, update its values
                            values.update(value)
                        else:
                            # for single value, add it to the dict
                            values[p.get_name()] = value

                for param in self.body_parameters:
                    update_values(param)

                if len(values) > 0:
                    return "data", values
            elif isinstance(first_body_param.annot, PydanticXmlBody):
                # there is one PydanticXmlBody parameter
                assert (
                    pydantic_xml is not None
                ), "pydantic-xml must be installed to use PydanticXmlBody"
                if (value := first_body_param.get_value(ba)) is not None:
                    assert isinstance(value, pydantic_xml.BaseXmlModel)
                    return "content", value.to_xml()
            elif isinstance(first_body_param.annot, PydanticBody):
                # there is one PydanticBody parameter
                if (value := first_body_param.get_value(ba)) is not None:
                    assert isinstance(value, BaseModel)
                    return "content", value.model_dump_json(by_alias=True)
            elif isinstance(first_body_param.annot, JsonBody):
                # there is one JsonBody parameter
                if (value := first_body_param.get_value(ba)) is not None:
                    assert isinstance(value, dict)
                    return "json", value
            else:
                # there is one content parameter
                if (value := first_body_param.get_value(ba)) is not None:
                    return "content", value

        return (None, None)


class RapidApi:
    """
    Base class for API clients.

    This class represents an API client. Subclasses should define methods
    decorated with @http (or @get, @post, etc.) which represent API endpoints.

    Example:
        >>> from rapid_api_client import RapidApi, get, post
        >>> from typing import Annotated
        >>>
        >>> class MyApi(RapidApi):
        ...     @get("/users/{user_id}")
        ...     def get_user(self, user_id: Annotated[int, Path()]): ...
        ...
        ...     @post("/users")
        ...     def create_user(self, user: Annotated[dict, JsonBody()]): ...
        >>>
        >>> api = MyApi(base_url="https://api.example.com")
        >>> user = api.get_user(123)
    """

    def __init__(
        self,
        *,
        client: Client | None = None,
        async_client: AsyncClient | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a RapidApi instance.

        Args:
            client: An existing httpx.Client instance to use for synchronous requests
            async_client: An existing httpx.AsyncClient instance to use for asynchronous requests
            **kwargs: Additional arguments to pass to the httpx.Client and httpx.AsyncClient
                     constructors when creating new clients. Common arguments include:
                     - base_url: The base URL for the API
                     - headers: Default headers to include in all requests
                     - timeout: Default timeout for requests
        """
        self._client: Client | None = client
        self._async_client: AsyncClient | None = async_client
        self.client_factory_args: Dict[str, Any] = kwargs

    @property
    def client(self) -> Client:
        """
        Get the synchronous HTTP client.

        If no client was provided in the constructor, a new one is created
        using the arguments provided in the constructor.

        Returns:
            The httpx.Client instance for making synchronous requests
        """
        if self._client is None:
            self._client = Client(**self.client_factory_args)
        return self._client

    @property
    def async_client(self) -> AsyncClient:
        """
        Get the asynchronous HTTP client.

        If no async client was provided in the constructor, a new one is created
        using the arguments provided in the constructor.

        Returns:
            The httpx.AsyncClient instance for making asynchronous requests
        """
        if self._async_client is None:
            self._async_client = AsyncClient(**self.client_factory_args)
        return self._async_client
