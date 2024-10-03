from typing import Annotated

import pytest
from httpx import ReadTimeout
from pytest import mark

from rapid_api_client import Path, RapidApi, delete, get, patch, post, put
from tests.conftest import Infos


class HttpBinApi(RapidApi):
    @get("/delay/{delay}", response_class=Infos, timeout=3.5)
    async def delay(self, delay: Annotated[int, Path()]): ...

    @get("/anything", response_class=Infos)
    async def get(self): ...

    @post("/anything", response_class=Infos)
    async def post(self): ...

    @delete("/anything", response_class=Infos)
    async def delete(self): ...

    @put("/anything", response_class=Infos)
    async def put(self): ...

    @patch("/anything", response_class=Infos)
    async def patch(self): ...


@mark.asyncio
async def test_http_get(client):
    api = HttpBinApi(client)
    infos = await api.get()
    assert infos.method == "GET"


@mark.asyncio
async def test_http_post(client):
    api = HttpBinApi(client)
    infos = await api.post()
    assert infos.method == "POST"


@mark.asyncio
async def test_http_put(client):
    api = HttpBinApi(client)
    infos = await api.put()
    assert infos.method == "PUT"


@mark.asyncio
async def test_http_delete(client):
    api = HttpBinApi(client)
    infos = await api.delete()
    assert infos.method == "DELETE"


@mark.asyncio
async def test_http_patch(client):
    api = HttpBinApi(client)
    infos = await api.patch()
    assert infos.method == "PATCH"


@mark.asyncio
async def test_http_timeout(client):
    api = HttpBinApi(client)
    infos = await api.delay(3)
    assert str(infos.url) == "https://httpbin.org/delay/3"

    with pytest.raises(ReadTimeout):
        infos = await api.delay(4)
