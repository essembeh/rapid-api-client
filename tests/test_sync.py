from httpx import Client

from rapid_api_client import RapidApi, get

from .conftest import BASE_URL, Infos


class HttpBinApi(RapidApi):
    @get("/anything")
    def get(self) -> Infos: ...


def test_client():
    api = HttpBinApi(client=Client(base_url=BASE_URL))
    infos = api.get()
    assert infos.method == "GET"


def test_default_client():
    api = HttpBinApi(base_url=BASE_URL)
    infos = api.get()
    assert infos.method == "GET"
