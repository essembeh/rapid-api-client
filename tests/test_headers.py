from typing import Annotated

from rapid_api_client import Header, RapidApi, http
from tests.conftest import Infos


def test_header(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()]): ...

    infos = HttpBinApi(client).test("foo")
    assert infos.headers["Myheader"] == "foo"


def test_header_default(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()] = "bar"): ...

    infos = HttpBinApi(client).test("foo")
    assert infos.headers["Myheader"] == "foo"

    infos = HttpBinApi(client).test()
    assert infos.headers["Myheader"] == "bar"


def test_header_none(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str | None, Header()] = None): ...

    infos = HttpBinApi(client).test("foo")
    assert "Myheader" in infos.headers

    infos = HttpBinApi(client).test()
    assert "Myheader" not in infos.headers


def test_header_alias(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header(alias="otherheader")]): ...

    infos = HttpBinApi(client).test("foo")
    assert "Otherheader" in infos.headers
    assert "Myheader" not in infos.headers
