from dataclasses import dataclass

from httpx import HTTPError, Response
from pydantic import TypeAdapter
from pytest import mark, raises

from rapid_api_client import RapidApi
from rapid_api_client.async_ import get

from .conftest import HTTPBIN_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_response_raw(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything")
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 200


@mark.asyncio(loop_scope="module")
async def test_response_model(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert str(resp.url) == f"{HTTPBIN_URL}/anything"
    assert resp.method == "GET"
    assert isinstance(resp, Infos)


@mark.asyncio(loop_scope="module")
async def test_response_str(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=str)
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert resp.startswith("{")
    assert isinstance(resp, str)


@mark.asyncio(loop_scope="module")
async def test_response_bytes(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=bytes)
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert isinstance(resp, bytes)


@mark.asyncio(loop_scope="module")
async def test_response_typeadapter(async_client):
    @dataclass
    class Infos2:
        url: str
        method: str

    class HttpBinApi(RapidApi):
        @get("/anything", response_class=TypeAdapter(Infos2))
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert resp.url == f"{HTTPBIN_URL}/anything"
    assert resp.method == "GET"
    assert isinstance(resp, Infos2)


@mark.asyncio(loop_scope="module")
async def test_response_error(async_client):
    class HttpBinApi(RapidApi):
        @get("/status/500")
        def test(self): ...

    api = HttpBinApi(async_client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 500


@mark.asyncio(loop_scope="module")
async def test_response_error_raise(async_client):
    class HttpBinApi(RapidApi):
        @get("/status/500", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(async_client)

    with raises(HTTPError):
        await api.test()
