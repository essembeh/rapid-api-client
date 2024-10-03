from typing import Annotated

from pytest import mark

from rapid_api_client import Path, RapidApi, get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_path(client):
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}", response_class=Infos)
        def test(self, myparam: Annotated[str, Path()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"


@mark.asyncio(loop_scope="module")
async def test_path_default(client):
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}", response_class=Infos)
        def test(self, myparam: Annotated[str, Path()] = "bar"): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"

    infos = await api.test()
    assert infos.url.path == "/anything/bar"
