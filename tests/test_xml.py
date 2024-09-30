from typing import Annotated

from pydantic_xml import BaseXmlModel, attr
from pytest import mark

from rapid_api_client import RapidApi, get, post
from rapid_api_client.model import PydanticXmlBody
from tests.conftest import Infos


class XmlModel(BaseXmlModel, tag="slideshow"):
    title: str = attr("title")


@mark.asyncio
async def test_get_xml(client):
    class HttpBinApi(RapidApi):
        @get("/xml", response_class=XmlModel)
        async def test(self): ...

    api = HttpBinApi(client)

    model = await api.test()
    assert model.title == "Sample Slide Show"


@mark.asyncio
async def test_post_xml(client):
    class HttpBinApi(RapidApi):
        @post("/anything", response_class=Infos)
        async def test(self, xml: Annotated[XmlModel, PydanticXmlBody()]): ...

    api = HttpBinApi(client)

    infos = await api.test(XmlModel(title="Foobar"))
    assert infos.data == '<slideshow title="Foobar" />'
