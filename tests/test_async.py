import asyncio

from httpx import AsyncClient
from pytest import mark

from rapid_api_client import RapidApi, get

from .conftest import BASE_URL, Infos


class HttpBinApi(RapidApi):
    @get("/anything")
    async def get(self) -> Infos: ...


@mark.asyncio(loop_scope="module")
async def test_client():
    api = HttpBinApi(async_client=AsyncClient(base_url=BASE_URL))
    infos = await api.get()
    assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_default_client():
    api = HttpBinApi(base_url=BASE_URL)
    infos = await api.get()
    assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_taskgroup():
    api = HttpBinApi(base_url=BASE_URL)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(api.get()) for _ in range(3)]

    assert len(tasks) == 3
    for task in tasks:
        infos = task.result()
        assert infos.method == "GET"


@mark.asyncio(loop_scope="module")
async def test_gather():
    api = HttpBinApi(base_url=BASE_URL)

    asyncio.gather()
    tasks = await asyncio.gather(*[api.get() for _ in range(3)])

    assert len(tasks) == 3
    for infos in tasks:
        assert infos.method == "GET"
