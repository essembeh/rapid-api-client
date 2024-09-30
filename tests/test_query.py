from typing import Annotated

from rapid_api_client import Query, RapidApi, http
from tests.conftest import Infos


def test_query(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query()]): ...

    infos = HttpBinApi(client).test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"


def test_query_default(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query()] = "bar"): ...

    infos = HttpBinApi(client).test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = HttpBinApi(client).test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "bar"


def test_query_none(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str | None, Query()] = None): ...

    infos = HttpBinApi(client).test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["myparam"] == "foo"

    infos = HttpBinApi(client).test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 0


def test_query_alias(client):
    class HttpBinApi(RapidApi):
        @http("/anything", response_class=Infos)
        def test(self, myparam: Annotated[str, Query(alias="otherparam")]): ...

    infos = HttpBinApi(client).test("foo")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 1
    assert query_params["otherparam"] == "foo"
