from typing import Annotated, Literal

from pydantic import ValidationError
from pytest import mark, raises

from rapid_api_client import Header, Path, Query, RapidApi, get
from tests.conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_validation_path_fieldinfo(client):
    class MyApi(RapidApi):
        @get("/anything/{param}", response_class=Infos)
        def test(self, param: Annotated[str, Path(pattern="[a-z]+")]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    assert str(resp.url) == "https://httpbin.org/anything/foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_path_annotation(client):
    class MyApi(RapidApi):
        @get("/anything/{param}", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Path()]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    assert str(resp.url) == "https://httpbin.org/anything/foo"

    with raises(ValidationError):
        await api.test("baz")


@mark.asyncio(loop_scope="module")
async def test_validation_query_fieldinfo(client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[str, Query(pattern="[a-z]+")]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_query_annotation(client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Query()]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    query_params = dict(resp.url.query_params())
    assert len(query_params) == 1
    assert query_params["param"] == "foo"

    with raises(ValidationError):
        await api.test("baz")


@mark.asyncio(loop_scope="module")
async def test_validation_header_fieldinfo(client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[str, Header(pattern="[a-z]+")]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    assert resp.headers["Param"] == "foo"

    with raises(ValidationError):
        await api.test("FOO")


@mark.asyncio(loop_scope="module")
async def test_validation_header_annotation(client):
    class MyApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, param: Annotated[Literal["foo", "bar"], Header()]): ...

    api = MyApi(client)

    resp = await api.test("foo")
    assert resp.headers["Param"] == "foo"

    with raises(ValidationError):
        await api.test("baz")
