from dataclasses import dataclass

from httpx import HTTPError, Response
from pydantic import BaseModel
from pytest import mark, raises

from rapid_api_client import RapidApi, ResponseModel, get

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

        @get("/status/500", raise_for_status=True)
        async def raw_with_raise(self) -> Response: ...

        @get("/status/500", raise_for_status=False)
        async def raw_without_raise(self) -> Response: ...

        @get("/status/500")
        async def parsed(self) -> str: ...

        @get("/status/500", raise_for_status=True)
        async def parsed_with_raise(self) -> str: ...

        @get("/status/500", raise_for_status=False)
        async def parsed_without_raise(self) -> str: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp = await api.raw()
    assert resp.status_code == 500

    with raises(HTTPError):
        await api.raw_with_raise()

    resp = await api.raw_without_raise()
    assert resp.status_code == 500

    with raises(HTTPError):
        await api.parsed()

    with raises(HTTPError):
        await api.parsed_with_raise()

    infos = await api.parsed_without_raise()
    assert isinstance(infos, str)


@mark.asyncio(loop_scope="module")
async def test_response_rapidresponse():
    class MyModel(BaseModel):
        url: str
        method: str

    class MyModelWithResponse(ResponseModel):
        url: str
        method: str

    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test_model(self) -> MyModel: ...
        @get("/anything")
        async def test_with_response(self) -> MyModelWithResponse: ...

    api = HttpBinApi(base_url=BASE_URL)

    resp1 = await api.test_model()
    assert isinstance(resp1, MyModel)
    assert not hasattr(resp1, "_response")
    assert str(resp1.url) == f"{BASE_URL}/anything"
    assert resp1.method == "GET"

    resp2 = await api.test_with_response()
    assert isinstance(resp2, MyModelWithResponse)
    assert hasattr(resp2, "_response")
    assert isinstance(resp2._response, Response)
    assert resp2._response.status_code == 200
    assert str(resp2.url) == f"{BASE_URL}/anything"
    assert resp2.method == "GET"
