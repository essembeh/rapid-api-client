import os
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress

# local go-httpbin by default (see `just httpbin`), same implementation as https://httpbingo.org
BASE_URL = os.environ.get("HTTPBIN_URL", "https://httpbingo.org")


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
