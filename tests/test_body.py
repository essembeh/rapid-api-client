from typing import Annotated, Dict

from pydantic import BaseModel
from pytest import mark

from rapid_api_client import Body, FileBody, PydanticBody, RapidApi, post
from rapid_api_client.annotations import FormBody

from .conftest import Infos


@mark.asyncio(loop_scope="module")
async def test_body_str(client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        async def test(self, body: Annotated[str, Body()]): ...

    api = HttpBinApi(client)

    infos = await api.test("foo")
    assert infos.data == "foo"


@mark.asyncio(loop_scope="module")
async def test_body_form(client):
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(
            self,
            body: Annotated[Dict, FormBody()],
            extra: Annotated[str, FormBody(alias="extra_param")],
        ): ...

    api = HttpBinApi(client)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user, "foobar")
    assert len(infos.form) == 3
    assert infos.form["name"] == "John Doe"
    assert infos.form["age"] == "42"
    assert infos.form["extra_param"] == "foobar"


@mark.asyncio(loop_scope="module")
async def test_body_pydantic(client):
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(self, body: Annotated[User, PydanticBody()]): ...

    api = HttpBinApi(client)

    user = User(name="John Doe", age=42)
    infos = await api.test(user)
    user2 = User.model_validate_json(infos.data)
    assert user == user2


@mark.asyncio(loop_scope="module")
async def test_body_files(client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        def test(
            self,
            file1: Annotated[str, FileBody()],
            file2: Annotated[str, FileBody(alias="file2_alt")],
        ): ...

    api = HttpBinApi(client)

    infos = await api.test("content1", "content2")
    assert len(infos.files) == 2
    assert infos.files["file1"] == "content1"
    assert infos.files["file2_alt"] == "content2"
