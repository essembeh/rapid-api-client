from httpx import HTTPError, Response
from pytest import raises

from rapid_api_client import RapidApi, http
from tests.conftest import Infos


def test_response_raw(client):
    class HttpBinApi(RapidApi):
        @http("/anything")
        def test(self): ...

    resp = HttpBinApi(client).test()
    assert isinstance(resp, Response)
    assert resp.status_code == 200


def test_response_model(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self): ...

    resp = HttpBinApi(client).test()
    assert isinstance(resp, Infos)


def test_response_error(client):
    class HttpBinApi(RapidApi):
        @http("/status/500")
        def test(self): ...

    resp = HttpBinApi(client).test()
    assert isinstance(resp, Response)
    assert resp.status_code == 500


def test_response_error_raise(client):
    class HttpBinApi(RapidApi):
        @http("/status/500", response_class=Infos)
        def test(self): ...

    with raises(HTTPError):
        HttpBinApi(client).test()
