from typing import Any, Dict, List

from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress

BASE_URL = "https://httpbingo.org"


class Infos(BaseModel):
    args: Dict[str, Any]
    data: Any
    files: Dict[str, List[str]]
    form: Dict[str, List[str]]
    headers: Dict[str, List[str]]
    json_data: Dict[str, Any] | None = Field(alias="json", default=None)
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl
