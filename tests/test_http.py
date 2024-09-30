from rapid_api_client import RapidApi, delete, get, patch, post, put
from tests.conftest import Infos


class HttpBinApi(RapidApi):
    @get("/anything", response_class=Infos)
    def get(self): ...

    @post("/anything", response_class=Infos)
    def post(self): ...

    @delete("/anything", response_class=Infos)
    def delete(self): ...

    @put("/anything", response_class=Infos)
    def put(self): ...

    @patch("/anything", response_class=Infos)
    def patch(self): ...


def test_http_get(client):
    infos = HttpBinApi(client).get()
    assert infos.method == "GET"


def test_http_post(client):
    infos = HttpBinApi(client).post()
    assert infos.method == "POST"


def test_http_put(client):
    infos = HttpBinApi(client).put()
    assert infos.method == "PUT"


def test_http_delete(client):
    infos = HttpBinApi(client).delete()
    assert infos.method == "DELETE"


def test_http_patch(client):
    infos = HttpBinApi(client).patch()
    assert infos.method == "PATCH"
