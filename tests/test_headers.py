from typing import Annotated

from pytest import mark

from rapid_api_client import Header, RapidApi
from rapid_api_client.async_ import get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_header(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()]): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"


@mark.asyncio(loop_scope="module")
async def test_header_default(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(
            self,
            myheader: Annotated[str, Header(default="bar")],
            otherheader: Annotated[str, Header(default_factory=lambda: "BAR")],
        ): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo", "FOO")
    assert infos.headers["Myheader"] == "foo"
    assert infos.headers["Otherheader"] == "FOO"

    infos = await api.test()
    assert infos.headers["Myheader"] == "bar"
    assert infos.headers["Otherheader"] == "BAR"


@mark.asyncio(loop_scope="module")
async def test_header_default2(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()] = "bar"): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"

    infos = await api.test()
    assert infos.headers["Myheader"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_header_none(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(
            self,
            myheader: Annotated[str | None, Header(default=None)],
            myheader2: Annotated[str | None, Header()] = None,
        ): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo", "bar")
    assert infos.headers["Myheader"] == "foo"
    assert infos.headers["Myheader2"] == "bar"

    infos = await api.test()
    assert "Myheader" not in infos.headers
    assert "Myheader2" not in infos.headers


@mark.asyncio(loop_scope="module")
async def test_header_alias(async_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header(alias="otherheader")]): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert "Otherheader" in infos.headers
    assert "Myheader" not in infos.headers
