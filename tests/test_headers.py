from datetime import datetime, timezone
from typing import Annotated

from pydantic import ValidationError
from pytest import mark, raises

from rapid_api_client import Header, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_headers():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myheader: Annotated[str, Header()],
            myotherheader: Annotated[str, Header()],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "bar")
    assert infos.headers["Myheader"] == ["foo"]
    assert infos.headers["Myotherheader"] == ["bar"]


@mark.asyncio(loop_scope="module")
async def test_header_default_pydantic():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myheader: Annotated[str, Header(default="bar")]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == ["foo"]

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    assert infos.headers["Myheader"] == ["bar"]

    with raises(ValidationError):
        await api.test(None)


@mark.asyncio(loop_scope="module")
async def test_header_default_factory():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myheader: Annotated[str, Header(default_factory=lambda: "bar")],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == ["foo"]

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    assert infos.headers["Myheader"] == ["bar"]

    with raises(ValidationError):
        await api.test(None)


@mark.asyncio(loop_scope="module")
async def test_header_default_python():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myheader: Annotated[str, Header()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.headers["Myheader"] == ["foo"]

    infos = await api.test()
    assert infos.headers["Myheader"] == ["bar"]

    with raises(ValidationError):
        await api.test(None)


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


@mark.asyncio(loop_scope="module")
async def test_header_validation():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myheader: Annotated[str, Header(max_length=3)] = "bar"
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    for bad_value in ["foobar", "fooo", 42, None]:
        with raises(ValidationError):
            await api.test(bad_value)


@mark.asyncio(loop_scope="module")
async def test_header_transformer():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test_default(
            self, myheader: Annotated[datetime, Header()]
        ) -> Infos: ...

        @get("/anything")
        async def test_custom(
            self,
            myheader: Annotated[datetime, Header(transformer=lambda x: x.isoformat())],
        ) -> Infos: ...

        @get("/anything")
        async def test_foo(
            self, myheader: Annotated[datetime, Header(transformer=lambda x: "foo")]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    mydate = datetime(
        year=2020,
        month=12,
        day=30,
        hour=14,
        minute=42,
        second=12,
        tzinfo=timezone.utc,
    )

    resp_default = await api.test_default(mydate)
    assert resp_default.headers.get("Myheader") == ["2020-12-30 14:42:12+00:00"]

    resp_custom = await api.test_custom(mydate)
    assert resp_custom.headers.get("Myheader") == ["2020-12-30T14:42:12+00:00"]

    resp_foo = await api.test_foo(mydate)
    assert resp_foo.headers.get("Myheader") == ["foo"]
