from functools import partial
from typing import Annotated

from pydantic_xml import BaseXmlModel, attr, element
from pytest import MonkeyPatch, mark, raises

from rapid_api_client import PydanticXmlBody, RapidApi, ResponseModel, get, post

from .conftest import BASE_URL, Infos


class XmlModel(BaseXmlModel, tag="slideshow"):
    title: str = attr("title")


class XmlModelWithResponse(BaseXmlModel, ResponseModel, tag="slideshow"):
    title: str = attr("title")


@mark.asyncio(loop_scope="module")
async def test_get_xml() -> None:
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
async def test_post_xml() -> None:
    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "text/plain"})
        async def test(self, xml: Annotated[XmlModel, PydanticXmlBody()]) -> Infos: ...

    api = HttpBinApi(base_url=BASE_URL)

    infos_without_unset = await api.test(XmlModel(title="Foobar"))
    assert infos_without_unset.data == '<slideshow title="Foobar" />'


@mark.asyncio(loop_scope="module")
async def test_body_pydanticxml_serializer() -> None:
    class Data(BaseXmlModel, tag="data"):
        text_none: str | None = attr("text_null", default=None)
        text_empty: str | None = attr("text_empty", default="")
        text_default: str | None = attr("text_default", default="42")
        sub_empty: str | None = element("sub_empty", default="")
        sub_none: str | None = element("sub_none", default=None)
        sub_default: str | None = element("sub_default", default="42")

    class HttpBinApi(RapidApi):
        @post("/anything", headers={"content-type": "text/plain"})
        async def test(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    transformer=partial(
                        BaseXmlModel.to_xml,
                        skip_empty=False,
                        exclude_none=False,
                        exclude_unset=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def skip_empty(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    transformer=partial(
                        BaseXmlModel.to_xml,
                        skip_empty=True,
                        exclude_none=False,
                        exclude_unset=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def exclude_none(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    transformer=partial(
                        BaseXmlModel.to_xml,
                        skip_empty=False,
                        exclude_none=True,
                        exclude_unset=False,
                    )
                ),
            ],
        ) -> Infos: ...

        @post("/anything", headers={"content-type": "text/plain"})
        async def exclude_unset(
            self,
            body: Annotated[
                Data,
                PydanticXmlBody(
                    transformer=partial(
                        BaseXmlModel.to_xml,
                        skip_empty=False,
                        exclude_none=False,
                        exclude_unset=True,
                    )
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

    assert (await api.test(Data())).data == (
        '<data text_null="" text_empty="" text_default="42">'
        "<sub_empty /><sub_none /><sub_default>42</sub_default></data>"
    )
    assert (
        await api.skip_empty(Data())
    ).data == '<data text_empty="" text_default="42"><sub_default>42</sub_default></data>'
    assert (
        await api.exclude_none(Data())
    ).data == '<data text_empty="" text_default="42"><sub_empty /><sub_default>42</sub_default></data>'
    assert (await api.exclude_unset(Data(text_none=None))).data == '<data text_null="" />'
    assert (
        await api.default_config(Data())
    ).data == '<data text_empty="" text_default="42"><sub_empty /><sub_default>42</sub_default></data>'


def test_pydanticxml_body_requires_pydantic_xml(monkeypatch: MonkeyPatch) -> None:
    """PydanticXmlBody must fail early with a clear error when pydantic-xml is not installed."""
    monkeypatch.setattr("rapid_api_client.xml.pydantic_xml", None)
    with raises(ImportError, match="pydantic-xml must be installed"):
        PydanticXmlBody()
