from pytest import mark

from rapid_api_client import SyncRapidApi
from rapid_api_client.async_ import AsyncRapidApi
from rapid_api_client.async_ import get as async_get
from rapid_api_client.sync import get as sync_get

from .conftest import HTTPBIN_URL, Infos


class HttpBinApi(SyncRapidApi):
    @sync_get("/anything", response_class=Infos)
    async def get(self): ...


@mark.asyncio(loop_scope="module")
async def test_default_client():
    class MyHttpBinApi(AsyncRapidApi):
        @async_get(f"{HTTPBIN_URL}/anything", response_class=Infos)
        async def get(self): ...

    api = MyHttpBinApi()
    resp = await api.get()
    assert resp.method == "GET"
