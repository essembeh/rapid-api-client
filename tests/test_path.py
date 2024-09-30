from typing import Annotated

from rapid_api_client import Path, RapidApi, http
from tests.conftest import Infos


def test_path(client):
    class HttpBinApi(RapidApi):
        @http("/anything/{myparam}", response_class=Infos)
        def test(self, myparam: Annotated[str, Path()]): ...

    infos = HttpBinApi(client).test("foo")
    assert infos.url.path == "/anything/foo"


def test_path_default(client):
    class HttpBinApi(RapidApi):
        @http("/anything/{myparam}", response_class=Infos)
        def test(self, myparam: Annotated[str, Path()] = "bar"): ...

    infos = HttpBinApi(client).test("foo")
    assert infos.url.path == "/anything/foo"

    infos = HttpBinApi(client).test()
    assert infos.url.path == "/anything/bar"
