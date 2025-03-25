from typing import Annotated

from pydantic_xml import BaseXmlModel, attr
from pytest import mark

from rapid_api_client import Header, PydanticXmlBody, RapidApi, get, post

from .conftest import BASE_URL, Infos


class XmlModel(BaseXmlModel, tag="slideshow"):
    title: str = attr("title")


@mark.asyncio(loop_scope="module")
async def test_get_xml():
    class HttpBinApi(RapidApi):
        @get("/xml")
        async def test(self) -> XmlModel: ...

    api = HttpBinApi(base_url=BASE_URL)

    model = await api.test()
    assert model.title == "Sample Slide Show"


@mark.asyncio(loop_scope="module")
async def test_post_xml():
    class HttpBinApi(RapidApi):
        @post("/anything")
        async def test(
            self,
            xml: Annotated[XmlModel, PydanticXmlBody()],
            content_type: Annotated[
                str, Header(alias="content-type", default="text/plain")
            ],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos = await api.test(XmlModel(title="Foobar"))  # pyright: ignore[reportCallIssue]
    assert infos.data == '<slideshow title="Foobar" />'
