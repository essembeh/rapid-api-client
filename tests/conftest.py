from typing import Any, Dict

import pytest
from httpx import Client
from pydantic import BaseModel, HttpUrl, IPvAnyAddress


class Infos(BaseModel):
    args: Dict[str, Any]
    data: Any
    files: Dict[str, str]
    headers: Dict[str, Any]
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl


@pytest.fixture
def client() -> Client:
    return Client(base_url="https://httpbin.org")
