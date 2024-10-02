from dataclasses import dataclass, field
from functools import partial, wraps
from inspect import Signature, signature
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Self,
    Tuple,
    Type,
    TypeVar,
    overload,
)

from httpx import AsyncClient, Request, Response
from pydantic import BaseModel, TypeAdapter
from pydantic_xml import BaseXmlModel

from .model import Body, FileBody, Header, Path, Query, RapidApi
from .utils import filter_none_values, find_annotation

BM = TypeVar("BM", bound=BaseModel)
T = TypeVar("T")


@dataclass
class CustomParameters:
    path: Dict[str, Path] = field(default_factory=dict)
    query: Dict[str, Query] = field(default_factory=dict)
    headers: Dict[str, Header] = field(default_factory=dict)
    body: Dict[str, Body] = field(default_factory=dict)

    @classmethod
    def from_sig(cls, signature: Signature) -> Self:
        out = cls()
        for parameter in signature.parameters.values():
            if (annot := find_annotation(parameter, Path)) is not None:
                out.path[parameter.name] = annot
            if (annot := find_annotation(parameter, Query)) is not None:
                out.query[parameter.name] = annot
            if (annot := find_annotation(parameter, Header)) is not None:
                out.headers[parameter.name] = annot
            if (annot := find_annotation(parameter, Body)) is not None:
                out.body[parameter.name] = annot
        return out


def build_request(
    client: AsyncClient,
    signature: Signature,
    parameters: CustomParameters,
    method: str,
    path: str,
    args: Tuple[Any],
    kwargs: Mapping[str, Any],
) -> Request:
    # valuate arguments with default values
    ba = signature.bind(*args, **kwargs)
    ba.apply_defaults()

    # resolve the api path
    path = path.format(**{k: ba.arguments[k] for k in parameters.path})

    headers = filter_none_values(
        {
            annot.alias or param: ba.arguments[param]
            for param, annot in parameters.headers.items()
        }
    )
    params = filter_none_values(
        {
            annot.alias or param: ba.arguments[param]
            for param, annot in parameters.query.items()
        }
    )
    content = None
    files = {}
    for param, annot in parameters.body.items():
        if (value := ba.arguments[param]) is not None:
            if isinstance(annot, FileBody):
                files[annot.alias or param] = annot.serialize(value)
            else:
                content = annot.serialize(value)

    return client.build_request(
        method, path, headers=headers, params=params, content=content, files=files
    )


def handle_response(
    response: Response,
    response_class: Type[Response | str | bytes | BM] | TypeAdapter[T],
) -> Response | str | bytes | BM | T:
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


@overload
def http(
    method: str, path: str, response_class: Type[Response] = Response
) -> Callable[[Callable], Callable[..., Awaitable[Response]]]: ...


@overload
def http(
    method: str, path: str, response_class: Type[str]
) -> Callable[[Callable], Callable[..., Awaitable[str]]]: ...


@overload
def http(
    method: str, path: str, response_class: Type[bytes]
) -> Callable[[Callable], Callable[..., Awaitable[bytes]]]: ...


@overload
def http(
    method: str, path: str, response_class: Type[BM]
) -> Callable[[Callable], Callable[..., Awaitable[BM]]]: ...


@overload
def http(
    method: str, path: str, response_class: TypeAdapter[T]
) -> Callable[[Callable], Callable[..., Awaitable[T]]]: ...


def http(
    method: str,
    path: str,
    response_class: Type[BM | str | bytes | Response] | TypeAdapter[T] = Response,
) -> Callable[[Callable], Callable[..., Awaitable[BM | str | bytes | Response | T]]]:
    def decorator(
        func: Callable,
    ) -> Callable[..., Awaitable[BM | str | bytes | Response | T]]:
        sig = signature(func)
        custom_parameters = CustomParameters.from_sig(sig)

        @wraps(func)
        async def wrapper(*args, **kwargs) -> BM | str | bytes | Response | T:
            assert isinstance(
                args[0], RapidApi
            ), f"{args[0]} should be an instance of RapidApi"
            client = args[0].client
            request = build_request(
                client, sig, custom_parameters, method, path, args, kwargs
            )
            response = await client.send(request)
            return handle_response(response, response_class)

        return wrapper

    return decorator


get = partial(http, "GET")
post = partial(http, "POST")
delete = partial(http, "DELETE")
put = partial(http, "PUT")
patch = partial(http, "PATCH")
