from pytest import mark, raises

from rapid_api_client import RapidApi, get


@mark.asyncio(loop_scope="module")
async def test_response_unsupported(client):
    class HttpBinApi(RapidApi):
        @get("/anything", response_class=int)  # pyright: ignore
        def test(self): ...

    api = HttpBinApi(client)

    with raises(ValueError):
        await api.test()  # pyright: ignore


@mark.asyncio(loop_scope="module")
async def test_bad_constructor(client):
    class HttpBinApi:
        @get("/anything")
        def test(self): ...

    api = HttpBinApi()
    with raises(ValueError):
        await api.test()
