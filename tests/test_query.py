from typing import Annotated

from pytest import mark

from rapid_api_client import Query, RapidApi, http
from tests.conftest import Infos


@mark.asyncio
async def test_query(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"


@mark.asyncio
async def test_query_default(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
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


@mark.asyncio
async def test_query_none(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str | None, Query()] = None): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = await api.test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 0


@mark.asyncio
async def test_query_alias(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query(alias="otherparam")]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["otherparam"] == "foo"
