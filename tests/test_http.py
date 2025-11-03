from typing import Annotated

from httpx import AsyncClient, ReadTimeout
from pytest import mark, raises

from rapid_api_client import Path, RapidApi, delete, get, patch, post, put

from .conftest import BASE_URL, Infos


class HttpBinApi(RapidApi):
    @get("/anything")
    async def get(self) -> Infos: ...

    @post("/anything")
    async def post(self) -> Infos: ...

    @delete("/anything")
    async def delete(self) -> Infos: ...

    @put("/anything")
    async def put(self) -> Infos: ...

    @patch("/anything")
    async def patch(self) -> Infos: ...


@mark.asyncio(loop_scope="module")
async def test_http_get():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.get()
    assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_http_post():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.post()
    assert infos.method == "POST"


@mark.asyncio(loop_scope="module")
async def test_http_put():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.put()
    assert infos.method == "PUT"


@mark.asyncio(loop_scope="module")
async def test_http_delete():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.delete()
    assert infos.method == "DELETE"


@mark.asyncio(loop_scope="module")
async def test_http_patch():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.patch()
    assert infos.method == "PATCH"


@mark.asyncio(loop_scope="module")
async def test_http_timeout():
    class HttpBinApi(RapidApi):
        @get("/delay/{delay}")
        async def delay(self, delay: Annotated[int, Path()]) -> Infos: ...

        @get("/delay/{delay}", timeout=1.5)
        async def delay2(self, delay: Annotated[int, Path()]) -> Infos: ...

    api = HttpBinApi(async_client=AsyncClient(base_url=BASE_URL, timeout=2.5))

    infos = await api.delay(1)
    assert str(infos.url) == f"{BASE_URL}/delay/1"

    # default timeout has been set to 2.5
    await api.delay(2)
    with raises(ReadTimeout):
        await api.delay(3)

    # function timeout has been set to 1.5
    await api.delay2(1)
    with raises(ReadTimeout):
        await api.delay2(2)


@mark.asyncio(loop_scope="module")
async def test_request_update():
    class HttpBinApiWithUpdate(RapidApi):
        def build_request(self, client, *, method: str, url: str, **kwargs):
            request = super().build_request(client, method=method, url=url, **kwargs)
            request.headers["Myheader"] = "foo"
            return request

        @get("/anything")
        async def with_update(self) -> Infos: ...

    class HttpBinApiWithoutUpdate(RapidApi):
        @get("/anything")
        async def without_update(self) -> Infos: ...

    api_with = HttpBinApiWithUpdate(base_url=BASE_URL)
    api_without = HttpBinApiWithoutUpdate(base_url=BASE_URL)

    resp1 = await api_with.with_update()
    assert resp1.headers.get("Myheader") == ["foo"]

    resp2 = await api_without.without_update()
    assert resp2.headers.get("Myheader") is None
