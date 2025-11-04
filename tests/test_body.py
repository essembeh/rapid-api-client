from functools import partial
from typing import Annotated, Dict, Optional

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
            content_type: Annotated[str, Header(alias="content-type")] = "text/plain",
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test("foo")
    assert infos.data == "foo"


@mark.asyncio(loop_scope="module")
async def test_body_json():
    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            body: Annotated[Dict, JsonBody()],
            content_type: Annotated[
                str, Header(alias="content-type")
            ] = "application/json",
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    user = {"name": "John Doe", "age": 42}
    infos = await api.test(user)
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
    infos = await api.test(user)
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


@mark.asyncio(loop_scope="module")
async def test_body_pydantic_transformer():
    class Data(BaseModel):
        text_none: Optional[str] = None
        text_empty: Optional[str] = ""
        text_default: Optional[str] = "42"

    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "application/json"})
        async def test(
            self,
            body: Annotated[
                Data,
                PydanticBody(
                    transformer=partial(
                        BaseModel.model_dump_json,
                        exclude_unset=False,
                        exclude_defaults=False,
                        exclude_none=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "application/json"})
        async def exclude_unset(
            self,
            body: Annotated[
                Data,
                PydanticBody(
                    transformer=partial(
                        BaseModel.model_dump_json,
                        exclude_unset=True,
                        exclude_defaults=False,
                        exclude_none=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "application/json"})
        async def exclude_defaults(
            self,
            body: Annotated[
                Data,
                PydanticBody(
                    transformer=partial(
                        BaseModel.model_dump_json,
                        exclude_unset=False,
                        exclude_defaults=True,
                        exclude_none=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "application/json"})
        async def exclude_none(
            self,
            body: Annotated[
                Data,
                PydanticBody(
                    transformer=partial(
                        BaseModel.model_dump_json,
                        exclude_unset=False,
                        exclude_defaults=False,
                        exclude_none=True,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "application/json"})
        async def default_config(
            self, body: Annotated[Data, PydanticBody()]
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    assert (
        await api.test(Data())
    ).data == '{"text_none":null,"text_empty":"","text_default":"42"}'
    assert (await api.exclude_unset(Data())).data == "{}"
    assert (
        await api.exclude_defaults(
            Data(text_default="42", text_empty="", text_none=None)
        )
    ).data == "{}"
    assert (
        await api.exclude_none(Data())
    ).data == '{"text_empty":"","text_default":"42"}'
    assert (
        await api.default_config(Data(text_default=None))
    ).data == '{"text_empty":""}'
    assert (
        await api.default_config(Data())
    ).data == '{"text_empty":"","text_default":"42"}'
