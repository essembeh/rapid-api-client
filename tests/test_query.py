from datetime import datetime, timezone
from typing import Annotated

from pydantic import Field, ValidationError
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
            self, myparam: Annotated[str, Query(), Field(default="bar")]
        ) -> Infos: ...

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
async def test_query_default_factory():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self, myparam: Annotated[str, Query(), Field(default_factory=lambda: "bar")]
        ) -> Infos: ...

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
            myparam: Annotated[str | None, Query(), Field(default=None)],
            myparam2: Annotated[str | None, Query()] = None,
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "bar")
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 2
    assert query_params["myparam"] == "foo"
    assert query_params["myparam2"] == "bar"

    infos = await api.test()
    query_params = dict(infos.url.query_params())
    assert len(query_params) == 0


@mark.asyncio(loop_scope="module")
async def test_query_alias():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test(
            self,
            myparam1: Annotated[str, Query(alias="mycustomparam1")],
            myparam2: Annotated[str, Query(), Field(alias="mycustomparam2")],
            myparam3: Annotated[
                str, Query(alias="mycustomparam3a"), Field(alias="mycustomparam3b")
            ],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo", "FOO", "bar")
    assert infos.args.get("mycustomparam1") == ["foo"]
    assert infos.args.get("mycustomparam2") == ["FOO"]
    assert infos.args.get("mycustomparam3a") == ["bar"]
    assert "myparam1" not in infos.args
    assert "myparam2" not in infos.args
    assert "myparam3" not in infos.args
    assert "mycustomparam3b" not in infos.args


@mark.asyncio(loop_scope="module")
async def test_query_alias2():
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
            self, myparam: Annotated[str, Query(), Field(max_length=3)] = "bar"
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    for bad_value in ["foobar", "fooo", 42, None]:
        with raises(ValidationError):
            await api.test(bad_value)


@mark.asyncio(loop_scope="module")
async def test_query_transformer():
    class HttpBinApi(RapidApi):
        @get("/anything")
        async def test_default(
            self, myparam: Annotated[datetime, Query()]
        ) -> Infos: ...

        @get("/anything")
        async def test_custom(
            self,
            myparam: Annotated[datetime, Query(transformer=lambda x: x.isoformat())],
        ) -> Infos: ...

        @get("/anything")
        async def test_foo(
            self, myparam: Annotated[datetime, Query(transformer=lambda x: "foo")]
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
    assert len(resp_default.args) == 1
    assert resp_default.args.get("myparam") == ["2020-12-30 14:42:12+00:00"]

    resp_custom = await api.test_custom(mydate)
    assert len(resp_custom.args) == 1
    assert resp_custom.args.get("myparam") == ["2020-12-30T14:42:12+00:00"]

    resp_foo = await api.test_foo(mydate)
    assert len(resp_foo.args) == 1
    assert resp_foo.args.get("myparam") == ["foo"]
