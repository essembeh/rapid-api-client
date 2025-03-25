import asyncio
from typing import Annotated, Any, Dict

from pydantic import BaseModel, HttpUrl, IPvAnyAddress

from rapid_api_client import (
    FormBody,
    Header,
    Path,
    PydanticBody,
    Query,
    RapidApi,
    get,
    post,
)


class Infos(BaseModel):
    args: Dict[str, Any]
    data: Any
    files: Dict[str, str]
    form: Dict[str, str]
    headers: Dict[str, Any]
    method: str | None = None
    origin: IPvAnyAddress
    url: HttpUrl


class User(BaseModel):
    name: str
    age: int


class HttpBinApi(RapidApi):
    @get("/anything/{path1}/{path2}")
    async def get(
        self,
        path1: Annotated[str, Path()],
        path2: Annotated[str, Path()],
        x_custom_header: Annotated[str | None, Header()] = None,
        sort: Annotated[str, Query()] = "asc",
    ) -> Infos: ...

    @post("/anything")
    async def post_form(
        self,
        field1: Annotated[str, FormBody()],
        field2: Annotated[str, FormBody()],
        extra_field: Annotated[Dict[str, str] | None, FormBody()] = None,
    ) -> Infos: ...

    @post("/anything")
    async def post_model(self, user: Annotated[User, PydanticBody()]) -> Infos: ...


async def main():
    api = HttpBinApi(base_url="https://httpbin.org")

    print("GET request:")
    infos = await api.get("foo", "bar", x_custom_header="foobar")
    print(infos.model_dump_json(indent=2))

    print("\nPOST form request:")
    infos = await api.post_form(
        "foo", "bar", extra_field={"extra": "field", "extra2": "field2"}
    )
    print(infos.model_dump_json(indent=2))

    print("\nPOST model request:")
    infos = await api.post_model(User(name="John", age=42))
    print(infos.model_dump_json(indent=2))
    User.model_validate_json(infos.data)


if __name__ == "__main__":
    asyncio.run(main())
