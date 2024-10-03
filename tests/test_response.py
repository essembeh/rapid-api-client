from dataclasses import dataclass

from httpx import HTTPError, Response
from pydantic import TypeAdapter
from pytest import mark, raises

from rapid_api_client import RapidApi, get
from tests.conftest import Infos


@mark.asyncio
async def test_response_raw(client):
    class HttpBinApi(RapidApi):
        @get("/anything")
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 200


@mark.asyncio
async def test_response_model(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert str(resp.url) == "https://httpbin.org/anything"
    assert resp.method == "GET"
    assert isinstance(resp, Infos)


@mark.asyncio
async def test_response_str(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=str)
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert resp.startswith("{")
    assert isinstance(resp, str)


@mark.asyncio
async def test_response_bytes(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=bytes)
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, bytes)


@mark.asyncio
async def test_response_typeadapter(client):
    @dataclass
    class Infos2:
        url: str
        method: str

    class HttpBinApi(RapidApi):
        @get("/anything", response_class=TypeAdapter(Infos2))
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert resp.url == "https://httpbin.org/anything"
    assert resp.method == "GET"
    assert isinstance(resp, Infos2)


@mark.asyncio
async def test_response_error(client):
    class HttpBinApi(RapidApi):
        @get("/status/500")
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 500


@mark.asyncio
async def test_response_error_raise(client):
    class HttpBinApi(RapidApi):
        @get("/status/500", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(client)

    with raises(HTTPError):
        await api.test()


@mark.asyncio
async def test_response_unsupported(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=int)
        def test(self): ...

    api = HttpBinApi(client)

    with raises(ValueError):
        await api.test()
