from typing import Annotated, Optional

from pydantic_xml import BaseXmlModel, attr, element
from pytest import mark

from rapid_api_client import PydanticXmlBody, RapidApi, ResponseModel, get, post

from .conftest import BASE_URL, Infos


class XmlModel(BaseXmlModel, tag="slideshow"):
    title: str = attr("title")


class XmlModelWithResponse(BaseXmlModel, ResponseModel, tag="slideshow"):
    title: str = attr("title")


@mark.asyncio(loop_scope="module")
async def test_get_xml():
    class HttpBinApi(RapidApi):
        @get("/xml")
        async def test(self) -> XmlModel: ...

        @get("/xml")
        async def test_with_response(self) -> XmlModelWithResponse: ...

    api = HttpBinApi(base_url=BASE_URL)

    model = await api.test()
    assert model.title == "Sample Slide Show"

    modelresponse = await api.test_with_response()
    assert modelresponse.title == "Sample Slide Show"
    assert isinstance(modelresponse, ResponseModel)
    assert hasattr(modelresponse, "_response")
    assert modelresponse._response.status_code == 200


@mark.asyncio(loop_scope="module")
async def test_post_xml():
    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "text/plain"})
        async def test(self, xml: Annotated[XmlModel, PydanticXmlBody()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos_without_unset = await api.test(XmlModel(title="Foobar"))
    assert infos_without_unset.data == '<slideshow title="Foobar" />'


@mark.asyncio(loop_scope="module")
async def test_body_pydanticxml_serializer():
    class Data(BaseXmlModel, tag="data"):
        text_none: Optional[str] = attr("text_null", default=None)
        text_empty: Optional[str] = attr("text_empty", default="")
        text_default: Optional[str] = attr("text_default", default="42")
        sub_empty: Optional[str] = element("sub_empty", default="")
        sub_none: Optional[str] = element("sub_none", default=None)
        sub_default: Optional[str] = element("sub_default", default="42")

    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "text/plain"})
        async def test(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    model_serializer_options={
                        "skip_empty": False,
                        "exclude_none": False,
                        "exclude_unset": False,
                    }
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def skip_empty(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    model_serializer_options={
                        "skip_empty": True,
                        "exclude_none": False,
                        "exclude_unset": False,
                    }
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def exclude_none(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    model_serializer_options={
                        "skip_empty": False,
                        "exclude_none": True,
                        "exclude_unset": False,
                    }
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def exclude_unset(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    model_serializer_options={
                        "skip_empty": False,
                        "exclude_none": False,
                        "exclude_unset": True,
                    }
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def default_config(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(),
            ],
        ) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    assert (
        (await api.test(Data())).data
        == '<data text_null="" text_empty="" text_default="42"><sub_empty /><sub_none /><sub_default>42</sub_default></data>'
    )
    assert (
        (await api.skip_empty(Data())).data
        == '<data text_empty="" text_default="42"><sub_default>42</sub_default></data>'
    )
    assert (
        (await api.exclude_none(Data())).data
        == '<data text_empty="" text_default="42"><sub_empty /><sub_default>42</sub_default></data>'
    )
    assert (
        await api.exclude_unset(Data(text_none=None))
    ).data == '<data text_null="" />'
    assert (
        (await api.default_config(Data())).data
        == '<data text_empty="" text_default="42"><sub_empty /><sub_default>42</sub_default></data>'
    )
