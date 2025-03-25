from typing import Annotated, Literal

from pydantic import ValidationError
from pytest import mark, raises

from rapid_api_client import Header, Path, Query, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_validation_path_fieldinfo():
    class MyApi(RapidApi):
        @get("/anything/{param}")
        async def test(
            self, param: Annotated[str, Path(pattern="[a-z]+")]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    assert str(resp.url) == f"{BASE_URL}/anything/foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_path_annotation():
    class MyApi(RapidApi):
        @get("/anything/{param}")
        async def test(
            self, param: Annotated[Literal["foo", "bar"], Path()]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    assert str(resp.url) == f"{BASE_URL}/anything/foo"

    with raises(ValidationError):
        await api.test("baz")  # pyright: ignore[reportArgumentType]


@mark.asyncio(loop_scope="module")
async def test_validation_query_fieldinfo():
    class MyApi(RapidApi):
        @get("/anything")
        async def test(
            self, param: Annotated[str, Query(pattern="[a-z]+")]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_query_annotation():
    class MyApi(RapidApi):
        @get("/anything")
        async def test(
            self, param: Annotated[Literal["foo", "bar"], Query()]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("baz")  # pyright: ignore[reportArgumentType]


@mark.asyncio(loop_scope="module")
async def test_validation_header_fieldinfo():
    class MyApi(RapidApi):
        @get("/anything")
        async def test(
            self, param: Annotated[str, Header(pattern="[a-z]+")]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    assert resp.headers["Param"] == ["foo"]

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_header_annotation():
    class MyApi(RapidApi):
        @get("/anything")
        async def test(
            self, param: Annotated[Literal["foo", "bar"], Header()]
        ) -> Infos: ...

    api = MyApi(base_url=BASE_URL)

    resp = await api.test("foo")
    assert resp.headers["Param"] == ["foo"]

    with raises(ValidationError):
        await api.test("baz")  # pyright: ignore[reportArgumentType]
