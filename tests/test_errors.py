from typing import Annotated

from httpx import Response, UnsupportedProtocol
from pytest import mark, raises

from rapid_api_client import Header, RapidApi, get

from .conftest import BASE_URL


@mark.asyncio(loop_scope="module")
async def test_response_unsupported():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> int: ...

    api = HttpBinApi(base_url=BASE_URL)

    with raises(ValueError):
        await api.test()


@mark.asyncio(loop_scope="module")
async def test_bad_constructor():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> Response: ...

    api = HttpBinApi()

    with raises(UnsupportedProtocol):
        await api.test()


@mark.asyncio(loop_scope="module")
async def test_missing_parameter():
    class HttpBinApi(RapidApi):
        @get("/anything")
        def test(self, header: Annotated[str, Header()]): ...

    api = HttpBinApi(base_url=BASE_URL)
    with raises(ValueError):
        await api.test()  # pyright: ignore[reportCallIssue]
