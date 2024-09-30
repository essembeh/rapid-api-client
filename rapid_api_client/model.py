from dataclasses import dataclass, field
from typing import Any

from httpx import Client
from pydantic import BaseModel


@dataclass
class RapidApi:
    client: Client = field(default_factory=Client)


class CustomParameter: ...


class Path(CustomParameter): ...


@dataclass
class Query(CustomParameter):
    alias: str | None = None


@dataclass
class Header(CustomParameter):
    alias: str | None = None


class Body(CustomParameter):
    def serialize(self, body: Any) -> str | bytes:
        return body


@dataclass
class FileBody(Body):
    alias: str | None = None

    def serialize(self, body: Any) -> str | bytes:
        return body


@dataclass
class PydanticBody(Body):
    prettyprint: bool = False

    def serialize(self, body: Any) -> str | bytes:
        assert isinstance(body, BaseModel)
        return body.model_dump_json(indent=2 if self.prettyprint else None)
