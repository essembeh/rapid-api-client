from typing import Annotated

from pytest import mark

from rapid_api_client import Path, RapidApi
from rapid_api_client.async_ import get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_path(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}", response_class=Infos)
        async def test(self, myparam: Annotated[str, Path()]): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"


@mark.asyncio(loop_scope="module")
async def test_path_default(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}", response_class=Infos)
        async def test(self, myparam: Annotated[str, Path()] = "bar"): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"

    infos = await api.test()
    assert infos.url.path == "/anything/bar"
