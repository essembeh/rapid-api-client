import asyncio

from pytest import mark

from rapid_api_client import RapidApi, get

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_taskgroup(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        async def get(self): ...

    api = HttpBinApi(client)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(api.get()) for _ in range(3)]

    assert len(tasks) == 3
    for task in tasks:
        infos = task.result()
        assert infos.method == "GET"
