from typing import Annotated

from pytest import mark

from rapid_api_client import Query, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_query():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(self, myparam: Annotated[str, Query()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"


@mark.asyncio(loop_scope="module")
async def test_query_default():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myparam: Annotated[str, Query(default="bar")],
            otherparam: Annotated[str, Query(default_factory=lambda: "BAR")],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "FOO")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 2
    assert query_params["myparam"] == "foo"
    assert query_params["otherparam"] == "FOO"

    infos = await api.test()  # pyright: ignore[reportCallIssue]
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 2
    assert query_params["myparam"] == "bar"
    assert query_params["otherparam"] == "BAR"


@mark.asyncio(loop_scope="module")
async def test_query_default2():
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
