from rapid_api_client import RapidApi, SyncRapidApi, get

from .conftest import HTTPBIN_URL, Infos


def test_get(sync_client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=Infos)
        def get(self): ...

    api = HttpBinApi(sync_client)
    infos = api.get()
    assert infos.method == "GET"


def test_default_client():
    class HttpBinApi(SyncRapidApi):
        @get(f"{HTTPBIN_URL}/anything", response_class=Infos)
        def get(self): ...

    api = HttpBinApi()
    resp = api.get()
    assert resp.method == "GET"
