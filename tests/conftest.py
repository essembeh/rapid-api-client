from typing import Any, Dict

import pytest
from httpx import AsyncClient, AsyncHTTPTransport, Client, HTTPTransport
from pydantic import BaseModel, Field, HttpUrl, IPvAnyAddress


class Infos(BaseModel):
    args: Dict[str, Any]
    data: Any
    files: Dict[str, str]
    form: Dict[str, str]
    headers: Dict[str, Any]
    json_data: Dict[str, Any] | None = Field(alias="json", default=None)
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl


@pytest.fixture(scope="module")
def async_client() -> AsyncClient:
    return AsyncClient(
        base_url="https://httpbin.org", transport=AsyncHTTPTransport(retries=5)
    )


@pytest.fixture(scope="module")
def sync_client() -> Client:
    return Client(base_url="https://httpbin.org", transport=HTTPTransport(retries=5))
