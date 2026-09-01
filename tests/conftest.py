from typing import Any

from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress

BASE_URL = "https://httpbingo.org"


class Infos(BaseModel):
    args: dict[str, Any]
    data: Any
    files: dict[str, list[str]]
    form: dict[str, list[str]]
    headers: dict[str, list[str]]
    json_data: dict[str, Any] | None = Field(alias="json", default=None)
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl
