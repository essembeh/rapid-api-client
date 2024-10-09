"""
rapid-api-client
"""

from importlib.metadata import version

from .annotations import (
    Body,
    FileBody,
    FormBody,
    Header,
    Path,
    PydanticBody,
    PydanticXmlBody,
    Query,
)
from .client import RapidApi
from .decorator import delete, get, http, patch, post, put

__version__ = version(__name__)
__all__ = [
    "Body",
    "delete",
    "FileBody",
    "FormBody",
    "get",
    "Header",
    "http",
    "patch",
    "Path",
    "post",
    "put",
    "PydanticBody",
    "PydanticXmlBody",
    "Query",
    "RapidApi",
]
