from dataclasses import dataclass, field
from functools import partial, wraps
from inspect import Signature, signature
from typing import Any, Awaitable, Callable, Dict, Mapping, Self, Tuple, Type, TypeVar

from httpx import AsyncClient, Request, Response
from pydantic import BaseModel

from .model import Body, FileBody, Header, Path, Query, RapidApi, pydantic_xml
from .utils import filter_none_values, find_annotation

RESP = TypeVar("RESP", bound=BaseModel | Response)


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


def http(
    path: str, method: str = "GET", response_class: Type[RESP] = Response
) -> Callable[[Callable], Callable[..., Awaitable[RESP]]]:
    def decorator(func: Callable) -> Callable[..., Awaitable[RESP]]:
        sig = signature(func)
        custom_parameters = CustomParameters.from_sig(sig)

        @wraps(func)
        async def wrapper(*args, **kwargs) -> RESP:
            assert isinstance(
                args[0], RapidApi
            ), f"{args[0]} should be an instance of RapidApi"
            client = args[0].client
            request = build_request(
                client, sig, custom_parameters, method, path, args, kwargs
            )
            response = await client.send(request)
            if pydantic_xml is not None and issubclass(
                response_class, pydantic_xml.BaseXmlModel
            ):
                response.raise_for_status()
                return response_class.from_xml(response.content)
            if issubclass(response_class, BaseModel):
                response.raise_for_status()
                return response_class.model_validate_json(response.content)
            return response

        return wrapper

    return decorator


get = partial(http, method="GET")
post = partial(http, method="POST")
delete = partial(http, method="DELETE")
put = partial(http, method="PUT")
patch = partial(http, method="PATCH")
