from httpx import HTTPError, Response
from pytest import mark, raises

from rapid_api_client import RapidApi, http
from tests.conftest import Infos


@mark.asyncio
async def test_response_raw(client):
    class HttpBinApi(RapidApi):
        @http("/anything")
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 200


@mark.asyncio
async def test_response_model(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, Infos)


@mark.asyncio
async def test_response_error(client):
    class HttpBinApi(RapidApi):
        @http("/status/500")
        def test(self): ...

    api = HttpBinApi(client)

    resp = await api.test()
    assert isinstance(resp, Response)
    assert resp.status_code == 500


@mark.asyncio
async def test_response_error_raise(client):
    class HttpBinApi(RapidApi):
        @http("/status/500", response_class=Infos)
        def test(self): ...

    api = HttpBinApi(client)

    with raises(HTTPError):
        await api.test()
