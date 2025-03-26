from typing import Annotated, Dict

from pydantic import BaseModel, Field
from pytest import mark, raises

from rapid_api_client import (
    Body,
    FileBody,
    FormBody,
    Header,
    JsonBody,
    PydanticBody,
    RapidApi,
    post,
)

from .conftest import BASE_URL, Infos


@mark.asyncio(loop_scope="module")
async def test_body_str():
    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            body: Annotated[str, Body()],
            content_type: Annotated[
                str, Header(alias="content-type", default="text/plain")
            ],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")  # pyright: ignore[reportCallIssue]
    assert infos.data == "foo"


@mark.asyncio(loop_scope="module")
async def test_body_json():
    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            body: Annotated[Dict, JsonBody()],
            content_type: Annotated[
                str, Header(alias="content-type", default="application/json")
            ],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user)  # pyright: ignore[reportCallIssue]
    assert infos.json_data is not None
    assert infos.json_data == user


@mark.asyncio(loop_scope="module")
async def test_body_form():
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            body: Annotated[Dict, FormBody()],
            extra: Annotated[str, FormBody(alias="extra_param")],
            default: Annotated[str, FormBody()] = "hello",
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user, "foobar")
    assert len(infos.form) == 4
    assert infos.form["name"] == ["John Doe"]
    assert infos.form["age"] == ["42"]
    assert infos.form["extra_param"] == ["foobar"]
    assert infos.form["default"] == ["hello"]


@mark.asyncio(loop_scope="module")
async def test_body_pydantic():
    class User(BaseModel):
        foo: str = Field(alias="firstname")
        bar: str = Field(alias="lastname")
        age: int

    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "application/json"})
        async def test(self, body: Annotated[User, PydanticBody()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    user = User(firstname="John", lastname="Doe", age=42)
    infos = await api.test(user)  # pyright: ignore[reportCallIssue]
    user2 = User.model_validate_json(infos.data)
    assert user == user2


@mark.asyncio(loop_scope="module")
async def test_body_files():
    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            file1: Annotated[str, FileBody()],
            file2: Annotated[str, FileBody(alias="file2_alt")],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("content1", "content2")
    assert len(infos.files) == 2
    assert infos.files["file1"] == ["content1"]
    assert infos.files["file2_alt"] == ["content2"]


@mark.asyncio(loop_scope="module")
async def test_body_mixed():
    with raises(AssertionError):

        class HttpBinApi1(RapidApi):
            @post("/anything")
            async def test(
                self,
                param1: Annotated[str, FileBody()],
                param2: Annotated[str, FormBody()],
            ) -> Infos: ...

    with raises(AssertionError):

        class HttpBinApi2(RapidApi):
            @post("/anything")
            async def test(
                self,
                param1: Annotated[str, Body()],
                param2: Annotated[str, Body()],
            ) -> Infos: ...
