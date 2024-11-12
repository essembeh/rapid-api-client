from typing import Annotated, Literal

from pydantic import ValidationError
from pytest import mark, raises

from rapid_api_client import Header, Path, Query, RapidApi
from rapid_api_client.async_ import get
from tests.conftest import HTTPBIN_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_validation_path_fieldinfo(async_client):
    class MyApi(RapidApi):
        @get("/anything/{param}", response_class=Infos)
        def test(self, param: Annotated[str, Path(pattern="[a-z]+")]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    assert str(resp.url) == f"{HTTPBIN_URL}/anything/foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_path_annotation(async_client):
    class MyApi(RapidApi):
        @get("/anything/{param}", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Path()]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    assert str(resp.url) == f"{HTTPBIN_URL}/anything/foo"

    with raises(ValidationError):
        await api.test("baz")


@mark.asyncio(loop_scope="module")
async def test_validation_query_fieldinfo(async_client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[str, Query(pattern="[a-z]+")]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_query_annotation(async_client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Query()]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("baz")


@mark.asyncio(loop_scope="module")
async def test_validation_header_fieldinfo(async_client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[str, Header(pattern="[a-z]+")]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    assert resp.headers["Param"] == ["foo"]

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_header_annotation(async_client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Header()]): ...

    api = MyApi(async_client)

    resp = await api.test("foo")
    assert resp.headers["Param"] == ["foo"]

    with raises(ValidationError):
        await api.test("baz")
