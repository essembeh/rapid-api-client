from typing import Annotated

from pydantic import ValidationError
from pytest import mark, raises

from rapid_api_client import Query, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_query():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myparam: Annotated[str, Query()],
            myotherparam: Annotated[str, Query()],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "bar")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 2
    assert query_params["myparam"] == "foo"
    assert query_params["myotherparam"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_query_default_pydantic():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myparam: Annotated[str, Query(default="bar")]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_query_default_factory():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myparam: Annotated[str, Query()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_query_default_python():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myparam: Annotated[str, Query()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_query_none():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myparam: Annotated[str | None, Query(default=None)],
            myparam2: Annotated[str | None, Query()] = None,
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "bar")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 2
    assert query_params["myparam"] == "foo"
    assert query_params["myparam2"] == "bar"

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 0


@mark.asyncio(loop_scope="module")
async def test_query_alias():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myparam: Annotated[str, Query(alias="otherparam")]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["otherparam"] == "foo"


@mark.asyncio(loop_scope="module")
async def test_query_validation():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myparam: Annotated[str, Query(max_length=3)] = "bar"
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    for bad_value in ["foobar", "fooo", 42, None]:
        with raises(ValidationError):
            await api.test(bad_value)
