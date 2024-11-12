from typing import Any, Dict, List

import pytest
from httpx import AsyncClient, Client
from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress

HTTPBIN_URL = "https://httpbingo.org"


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


@pytest.fixture(scope="module")
def sync_client() -> Client:
    return Client(base_url=HTTPBIN_URL)


@pytest.fixture(scope="module")
def async_client() -> AsyncClient:
    return AsyncClient(base_url=HTTPBIN_URL)
