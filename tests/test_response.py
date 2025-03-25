from dataclasses import dataclass

from httpx import HTTPError, Response
from pytest import mark, raises

from rapid_api_client import RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_response_raw():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self): ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 200


@mark.asyncio(loop_scope="module")
async def test_response_model():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert str(resp.url) == f"{BASE_URL}/anything"
    assert resp.method == "GET"
    assert isinstance(resp, Infos)


@mark.asyncio(loop_scope="module")
async def test_response_str():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> str: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert resp.startswith("{")
    assert isinstance(resp, str)


@mark.asyncio(loop_scope="module")
async def test_response_bytes():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> bytes: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert isinstance(resp, bytes)


@mark.asyncio(loop_scope="module")
async def test_response_dataclass():
    @dataclass
    class Infos2:
        url: str
        method: str

    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self) -> Infos2: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert isinstance(resp, Infos2)
    assert resp.url == f"{BASE_URL}/anything"
    assert resp.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_response_error():
    class HttpBinApi(RapidApi):
        @get("/status/500")
        async def test(self): ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 500


@mark.asyncio(loop_scope="module")
async def test_response_error_raise():
    class HttpBinApi(RapidApi):
        @get("/status/500")
        async def raw(self) -> Response: ...

        @get("/status/500")
        async def with_raise(self) -> Infos: ...

        @get("/status/500", raise_for_status=False)
        async def witout_raise(self) -> str: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.raw()
    assert resp.status_code == 500

    with raises(HTTPError):
        await api.with_raise()

    infos = await api.witout_raise()
    assert isinstance(infos, str)
