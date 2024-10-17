from typing import Annotated

from pytest import mark, raises

from rapid_api_client import Header, RapidApi
from rapid_api_client.async_ import get


@mark.asyncio(loop_scope="module")
async def test_response_unsupported(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=int)  # pyright: ignore
        def test(self): ...

    api = HttpBinApi(async_client)

    with raises(ValueError):
        await api.test()  # pyright: ignore


@mark.asyncio(loop_scope="module")
async def test_bad_constructor():
    class HttpBinApi:
        @get("/anything")
        def test(self): ...

    api = HttpBinApi()
    with raises(AssertionError):
        await api.test()


@mark.asyncio(loop_scope="module")
async def test_missing_parameter(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything")
        def test(self, header: Annotated[str, Header()]): ...

    api = HttpBinApi(async_client)
    with raises(ValueError):
        await api.test()
