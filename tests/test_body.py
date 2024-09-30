from typing import Annotated

from pydantic import BaseModel

from rapid_api_client import Body, FileBody, PydanticBody, http
from rapid_api_client.model import RapidApi
from tests.conftest import Infos


def test_body_str(client):
    class HttpBinApi(RapidApi):
        @http("/anything", method="POST", response_class=Infos)
        def test(self, body: Annotated[str, Body()]): ...

    infos = HttpBinApi(client).test("foo")
    assert infos.data == "foo"


def test_body_pydantic(client):
    class User(BaseModel):
        name: str
        age: int

    class HttpBinApi(RapidApi):
        @http("/anything", method="POST", response_class=Infos)
        def test(self, body: Annotated[User, PydanticBody()]): ...

    user = User(name="John Doe", age=42)
    infos = HttpBinApi(client).test(user)
    user2 = User.model_validate_json(infos.data)
    assert user == user2


def test_body_files(client):
    class HttpBinApi(RapidApi):
        @http("/anything", method="POST", response_class=Infos)
        def test(
            self,
            file1: Annotated[str, FileBody()],
            file2: Annotated[str, FileBody(alias="file2_alt")],
        ): ...

    infos = HttpBinApi(client).test("content1", "content2")
    assert len(infos.files) == 2
    assert infos.files["file1"] == "content1"
    assert infos.files["file2_alt"] == "content2"
