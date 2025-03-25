from typing import Annotated

from pytest import mark

from rapid_api_client import Header, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_header():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myheader: Annotated[str, Header()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == ["foo"]


@mark.asyncio(loop_scope="module")
async def test_header_default():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myheader: Annotated[str, Header(default="bar")],
            otherheader: Annotated[str, Header(default_factory=lambda: "BAR")],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "FOO")
    assert infos.headers["Myheader"] == ["foo"]
    assert infos.headers["Otherheader"] == ["FOO"]

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    assert infos.headers["Myheader"] == ["bar"]
    assert infos.headers["Otherheader"] == ["BAR"]


@mark.asyncio(loop_scope="module")
async def test_header_default2():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myheader: Annotated[str, Header()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == ["foo"]

    infos = await api.test()
    assert infos.headers["Myheader"] == ["bar"]


@mark.asyncio(loop_scope="module")
async def test_header_none():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myheader: Annotated[str | None, Header(default=None)],
            myheader2: Annotated[str | None, Header()] = None,
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "bar")
    assert infos.headers["Myheader"] == ["foo"]
    assert infos.headers["Myheader2"] == ["bar"]

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    assert "Myheader" not in infos.headers
    assert "Myheader2" not in infos.headers


@mark.asyncio(loop_scope="module")
async def test_header_alias():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myheader: Annotated[str, Header(alias="otherheader")]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert "Otherheader" in infos.headers
    assert "Myheader" not in infos.headers


@mark.asyncio(loop_scope="module")
async def test_header_override():
    class HttpBinApi(RapidApi):
        @get("/anything", headers={"myheader": "foo"})
        async def test(
            self, myheader: Annotated[str | None, Header()] = None
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test()
    assert infos.headers.get("Myheader") == ["foo"]

    infos = await api.test("bar")
    assert infos.headers.get("Myheader") == ["bar"]
