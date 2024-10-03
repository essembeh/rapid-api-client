from typing import Annotated

from pytest import mark

from rapid_api_client import Query, RapidApi, get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_query(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"


@mark.asyncio(loop_scope="module")
async def test_query_default(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query()] = "bar"): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "bar"


@mark.asyncio(loop_scope="module")
async def test_query_none(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str | None, Query()] = None): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 0


@mark.asyncio(loop_scope="module")
async def test_query_alias(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query(alias="otherparam")]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["otherparam"] == "foo"
