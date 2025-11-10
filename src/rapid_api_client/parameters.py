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
    Optional,
    Self,
    Tuple,
)

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .annotations import (
    Body,
    FileBody,
    FormBody,
    Header,
    Path,
    Query,
    RapidAnnotation,
)
from .errors import AnnotationError, FieldError, InvalidBodyError
from .utils import RA, filter_none_values, find_annotation


@dataclass(slots=True, frozen=True)
class RapidParameter(Generic[RA]):
    """
    Represents a function parameter with its associated annotation.

    This class is used internally to handle parameters that have been annotated
    with one of the annotation types (Path, Query, Header, Body, etc.).

    Attributes:
        param: The function parameter
        rapid_annotation: The annotation associated with the parameter
        fieldinfo_annotation: The optional Pydantic annotation
    """

    parameter: Parameter
    rapid_annotation: RA
    fieldinfo_annotation: Optional[FieldInfo]

    @property
    def name(self) -> str:
        """
        Get the original parameter name.

        Returns:
            The name of the parameter as defined in the function signature
        """
        return self.parameter.name

    def get_name(self) -> str:
        """
        Get the parameter name, using the alias if available

        Returns:
            The parameter name or its alias
        """
        if self.rapid_annotation.alias:
            return self.rapid_annotation.alias
        if self.fieldinfo_annotation and self.fieldinfo_annotation.alias:
            return self.fieldinfo_annotation.alias
        return self.name

    def get_value(self, ba: BoundArguments) -> Any:
        """
        Get the parameter value from bound arguments.

        This method retrieves the parameter value from the bound arguments,
        or uses the default value if the parameter is not in the arguments.
        The value is validated against the parameter's type annotation.
        The value is then transformed using the annotation's transformer function
        if one is defined.

        Args:
            ba: The bound arguments from the function call

        Returns:
            The parameter value, optionally transformed by the annotation's transformer

        Raises:
            ValueError: If the parameter has no value and no default
        """
        out = None
        if self.name in ba.arguments:
            out = ba.arguments.get(self.name)
        elif self.fieldinfo_annotation:
            # Use pydantic default value if available
            out = self.fieldinfo_annotation.get_default(call_default_factory=True)
            if out is PydanticUndefined:
                raise FieldError(f"Missing value for parameter {self.name}")

        # Use pydantic to validate the value
        out = TypeAdapter(self.parameter.annotation).validate_python(out)

        # If the value is not null and a transformer is set, use it
        if out is not None and self.rapid_annotation.transformer:
            out = self.rapid_annotation.transformer(out)

        return out


@dataclass(slots=True, frozen=True)
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
            if rapid_annotation := find_annotation(parameter, RapidAnnotation):
                fieldinfo_annotation = find_annotation(parameter, FieldInfo)
                if isinstance(rapid_annotation, Path):
                    out.path_parameters.append(
                        RapidParameter(
                            parameter=parameter,
                            rapid_annotation=rapid_annotation,
                            fieldinfo_annotation=fieldinfo_annotation,
                        )
                    )
                elif isinstance(rapid_annotation, Query):
                    out.query_parameters.append(
                        RapidParameter(
                            parameter=parameter,
                            rapid_annotation=rapid_annotation,
                            fieldinfo_annotation=fieldinfo_annotation,
                        )
                    )
                elif isinstance(rapid_annotation, Header):
                    out.header_parameters.append(
                        RapidParameter(
                            parameter=parameter,
                            rapid_annotation=rapid_annotation,
                            fieldinfo_annotation=fieldinfo_annotation,
                        )
                    )
                elif isinstance(rapid_annotation, Body):
                    out.body_parameters.append(
                        RapidParameter(
                            parameter=parameter,
                            rapid_annotation=rapid_annotation,
                            fieldinfo_annotation=fieldinfo_annotation,
                        )
                    )
                else:
                    raise AnnotationError(
                        f"Invalid parameter annotation: {rapid_annotation}"
                    )

        # consistency check for body parameters
        if len(out.body_parameters) > 0:
            first_body_param = out.body_parameters[0]
            if isinstance(first_body_param.rapid_annotation, (FileBody, FormBody)):
                # FileBody/FormBody: check 1+ parameters of type FileBody
                for other_param in out.body_parameters:
                    if not isinstance(
                        other_param.rapid_annotation,
                        type(first_body_param.rapid_annotation),
                    ):
                        raise InvalidBodyError(
                            f"All body parameters must be of type {first_body_param.rapid_annotation.__class__.__name__}"
                        )
            elif isinstance(first_body_param.rapid_annotation, Body):
                # Body: check 1 parameter of type Body
                if len(out.body_parameters) > 1:
                    raise InvalidBodyError(
                        f"Only one Body allowed for type {first_body_param.rapid_annotation.__class__.__name__}"
                    )

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

            if isinstance(first_body_param.rapid_annotation, FileBody):
                # Case "files", one or more files can be provided
                values = filter_none_values(
                    {p.get_name(): p.get_value(ba) for p in self.body_parameters}
                )
                if len(values) > 0:
                    return first_body_param.rapid_annotation.keyword, values
            elif isinstance(first_body_param.rapid_annotation, FormBody):
                # Case "data", one or more fields can be provided
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
                    return first_body_param.rapid_annotation.keyword, values
            else:
                # Other cases, only one parameter allowed
                if (value := first_body_param.get_value(ba)) is not None:
                    return first_body_param.rapid_annotation.keyword, value

        return (None, None)
