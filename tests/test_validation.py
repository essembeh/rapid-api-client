from typing import Annotated

from pydantic import Field, PositiveInt, ValidationError
from pytest import mark, raises

from rapid_api_client import Header, Path, Query, RapidApi, get

from .conftest import BASE_URL, Infos


class MyApi(RapidApi):
    @get("/anything/{param}")
    async def test_path(
        self, param: Annotated[PositiveInt, Path(), Field(le=12)]
    ) -> Infos: ...

    @get("/anything")
    async def test_query(
        self, param: Annotated[PositiveInt, Query(), Field(le=12)]
    ) -> Infos: ...

    @get("/anything")
    async def test_header(
        self, param: Annotated[PositiveInt, Header(), Field(le=12)]
    ) -> Infos: ...


@mark.asyncio(loop_scope="module")
async def test_validation_path():
    api = MyApi(base_url=BASE_URL)

    await api.test_path(1)
    for value in [-1, 42, "FOO", None]:
        with raises(ValidationError):
            await api.test_path(value)


@mark.asyncio(loop_scope="module")
async def test_validation_header():
    api = MyApi(base_url=BASE_URL)

    await api.test_header(1)
    for value in [-1, 42, "FOO", None]:
        with raises(ValidationError):
            await api.test_header(value)


@mark.asyncio(loop_scope="module")
async def test_validation_query():
    api = MyApi(base_url=BASE_URL)

    await api.test_query(1)
    for value in [-1, 42, "FOO", None]:
        with raises(ValidationError):
            await api.test_query(value)
