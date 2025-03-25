from typing import Annotated

from pytest import mark

from rapid_api_client import Path, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_path():
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}")
        async def test(self, myparam: Annotated[str, Path()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"


@mark.asyncio(loop_scope="module")
async def test_path_default():
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}")
        async def test(self, myparam: Annotated[str, Path()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"

    infos = await api.test()
    assert infos.url.path == "/anything/bar"
