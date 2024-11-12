from typing import Annotated, Dict

from pydantic import BaseModel
from pytest import mark, raises

from rapid_api_client import Body, FileBody, FormBody, PydanticBody, RapidApi
from rapid_api_client.annotations import JsonBody
from rapid_api_client.async_ import post

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_body_str(async_client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        async def test(self, body: Annotated[str, Body()]): ...

    api = HttpBinApi(async_client)

    infos = await api.test("foo")
    assert infos.data == "foo"


@mark.asyncio(loop_scope="module")
async def test_body_json(async_client):
    class HttpBinApi(RapidApi):
        # @post("/anything")
        @post("/anything", response_class=Infos)
        async def test(self, body: Annotated[Dict, JsonBody()]): ...

    api = HttpBinApi(async_client)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user)
    assert infos.json_data is not None
    assert infos.json_data == user


@mark.asyncio(loop_scope="module")
async def test_body_form(async_client):
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(
            self,
            body: Annotated[Dict, FormBody()],
            extra: Annotated[str, FormBody(alias="extra_param")],
            default: Annotated[str, FormBody(default="hello")],
        ): ...

    api = HttpBinApi(async_client)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user, "foobar")
    assert len(infos.form) == 4
    assert infos.form["name"] == "John Doe"
    assert infos.form["age"] == "42"
    assert infos.form["extra_param"] == "foobar"
    assert infos.form["default"] == "hello"


@mark.asyncio(loop_scope="module")
async def test_body_pydantic(async_client):
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(self, body: Annotated[User, PydanticBody()]): ...

    api = HttpBinApi(async_client)

    user = User(name="John Doe", age=42)
    infos = await api.test(user)
    user2 = User.model_validate_json(infos.data)
    assert user == user2


@mark.asyncio(loop_scope="module")
async def test_body_files(async_client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(
            self,
            file1: Annotated[str, FileBody()],
            file2: Annotated[str, FileBody(alias="file2_alt")],
        ): ...

    api = HttpBinApi(async_client)

    infos = await api.test("content1", "content2")
    assert len(infos.files) == 2
    assert infos.files["file1"] == "content1"
    assert infos.files["file2_alt"] == "content2"


@mark.asyncio(loop_scope="module")
async def test_body_mixed(async_client):
    with raises(AssertionError):

        class HttpBinApi1(RapidApi):
            @post("/anything", response_class=Infos)
            def test(
                self,
                param1: Annotated[str, FileBody()],
                param2: Annotated[str, FormBody()],
            ): ...

    with raises(AssertionError):

        class HttpBinApi2(RapidApi):
            @post("/anything", response_class=Infos)
            def test(
                self,
                param1: Annotated[str, Body()],
                param2: Annotated[str, Body()],
            ): ...
