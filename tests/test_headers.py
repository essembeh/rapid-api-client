from typing import Annotated

from pytest import mark

from rapid_api_client import Header, RapidApi, get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_header(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"


@mark.asyncio(loop_scope="module")
async def test_header_default(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(
            self,
            myheader: Annotated[str, Header(default="bar")],
            otherheader: Annotated[str, Header(default_factory=lambda: "BAR")],
        ): ...

    api = HttpBinApi(client)

    infos = await api.test("foo", "FOO")
    assert infos.headers["Myheader"] == "foo"
    assert infos.headers["Otherheader"] == "FOO"

    infos = await api.test()
    assert infos.headers["Myheader"] == "bar"
    assert infos.headers["Otherheader"] == "BAR"


@mark.asyncio(loop_scope="module")
async def test_header_default2(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header()] = "bar"): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == "foo"

    infos = await api.test()
    assert infos.headers["Myheader"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_header_none(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str | None, Header(default=None)]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert "Myheader" in infos.headers

    infos = await api.test()
    assert "Myheader" not in infos.headers


@mark.asyncio(loop_scope="module")
async def test_header_alias(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myheader: Annotated[str, Header(alias="otherheader")]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert "Otherheader" in infos.headers
    assert "Myheader" not in infos.headers
