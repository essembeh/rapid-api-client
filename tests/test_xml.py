from typing import Annotated

from pydantic_xml import BaseXmlModel, attr
from pytest import mark

from rapid_api_client import PydanticXmlBody, RapidApi
from rapid_api_client.async_ import get, post

from .conftest import Infos


class XmlModel(BaseXmlModel, tag="slideshow"):
    title: str = attr("title")


@mark.asyncio(loop_scope="module")
async def test_get_xml(async_client):
    class HttpBinApi(RapidApi):
        @get("/xml", response_class=XmlModel)
        async def test(self): ...

    api = HttpBinApi(async_client)

    model = await api.test()
    assert model.title == "Sample Slide Show"


@mark.asyncio(loop_scope="module")
async def test_post_xml(async_client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        async def test(self, xml: Annotated[XmlModel, PydanticXmlBody()]): ...

    api = HttpBinApi(async_client)

    infos = await api.test(XmlModel(title="Foobar"))
    assert infos.data == '<slideshow title="Foobar" />'
