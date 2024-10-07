from typing import Any, Dict

import pytest
from httpx import AsyncClient, AsyncHTTPTransport
from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class Infos(BaseModel):
    args: Dict[str, Any]
    data: Any
    files: Dict[str, str]
    form: Dict[str, str]
    headers: Dict[str, Any]
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl


@pytest.fixture(scope="module")
def client() -> AsyncClient:
    return AsyncClient(
        base_url="https://httpbin.org", transport=AsyncHTTPTransport(retries=5)
    )
