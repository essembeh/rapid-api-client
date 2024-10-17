import asyncio

from pytest import mark

from rapid_api_client import RapidApi
from rapid_api_client.async_ import AsyncRapidApi, get

from .conftest import Infos


class HttpBinApi(RapidApi):
    @get("/anything", response_class=Infos)
    async def get(self): ...


@mark.asyncio(loop_scope="module")
async def test_taskgroup(async_client):
    api = HttpBinApi(async_client)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(api.get()) for _ in range(3)]

    assert len(tasks) == 3
    for task in tasks:
        infos = task.result()
        assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_gather(async_client):
    api = HttpBinApi(async_client)

    asyncio.gather()
    tasks = await asyncio.gather(*[api.get() for _ in range(3)])

    assert len(tasks) == 3
    for infos in tasks:
        assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_default_client():
    class MyHttpBinApi(AsyncRapidApi):
        @get("https://httpbin.org/anything", response_class=Infos)
        async def get(self): ...

    api = MyHttpBinApi()
    resp = await api.get()
    assert resp.method == "GET"
