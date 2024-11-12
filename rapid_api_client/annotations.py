"""
Model classes
"""

from pydantic.fields import FieldInfo


class BaseAnnotation(FieldInfo):
    """
    Meta class for annotations used to customize the request build
    """


class Path(BaseAnnotation):
    """
    Annotation to declare an argument used to resolve the api path/url
    """


class Query(BaseAnnotation):
    """
    Annotation to declare an argument used as a query parameter
    """


class Header(BaseAnnotation):
    """
    Annotation to declare an argument used as a request header
    """


class Body(BaseAnnotation):
    """
    Annotation to declare an argument used as http content for post/put/...
    """


class JsonBody(Body):
    """
    Annotation to declare an argument used as json objected for post/put/...
    """


class FormBody(Body):
    """
    Annotation to declare an argument used as url-encoded parameter
    If the annotated parameter is a Dict[str, str], its content will be merged to other form parameters,
    else, its name (or alias) and its serialized value will be added to the the other form parameters.
    """


class FileBody(Body):
    """
    Annotation to declare an argument used as file to be uploaded
    """


class PydanticBody(Body):
    """
    Annotation to declare an argument to be serialized to json and used as http content
    """


class PydanticXmlBody(PydanticBody):
    """
    Annotation to declare an argument to be serialized to xml and used as http content
    """
