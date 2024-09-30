from typing import Annotated

from pytest import mark

from rapid_api_client import Header, RapidApi, http
from tests.conftest import Infos


@mark.asyncio
async def test_header(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"


@mark.asyncio
async def test_header_default(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()] = "bar"): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"

    infos = await api.test()
    assert infos.headers["Myheader"] == "bar"


@mark.asyncio
async def test_header_none(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str | None, Header()] = None): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert "Myheader" in infos.headers

    infos = await api.test()
    assert "Myheader" not in infos.headers


@mark.asyncio
async def test_header_alias(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header(alias="otherheader")]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert "Otherheader" in infos.headers
    assert "Myheader" not in infos.headers
