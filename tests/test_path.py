from datetime import datetime, timezone
from typing import Annotated

from pytest import mark

from rapid_api_client import Path, RapidApi, get

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_path():
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}")
        async def test(self, myparam: Annotated[str, Path()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"


@mark.asyncio(loop_scope="module")
async def test_path_default():
    class HttpBinApi(RapidApi):
        @get("/anything/{myparam}")
        async def test(self, myparam: Annotated[str, Path()] = "bar") -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.url.path == "/anything/foo"

    infos = await api.test()
    assert infos.url.path == "/anything/bar"


@mark.asyncio(loop_scope="module")
async def test_path_transformer():
    class HttpBinApi(RapidApi):
        @get("/anything/{mypath}")
        async def test_default(self, mypath: Annotated[datetime, Path()]) -> Infos: ...

        @get("/anything/{mypath}")
        async def test_custom(
            self, mypath: Annotated[datetime, Path(transformer=lambda x: x.isoformat())]
        ) -> Infos: ...

        @get("/anything/{mypath}")
        async def test_foo(
            self, mypath: Annotated[datetime, Path(transformer=lambda x: "foo")]
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
    assert resp_default.url.path == "/anything/2020-12-30%2014:42:12+00:00"

    resp_custom = await api.test_custom(mydate)
    assert resp_custom.url.path == "/anything/2020-12-30T14:42:12+00:00"

    resp_foo = await api.test_foo(mydate)
    assert resp_foo.url.path == "/anything/foo"
