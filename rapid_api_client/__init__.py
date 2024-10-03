"""
rapid-api-client
"""

from importlib.metadata import version

from .annotations import Body, FileBody, Header, Path, PydanticBody, Query
from .client import RapidApi
from .decorator import delete, get, http, patch, post, put

__version__ = version(__name__)
__all__ = [
    "Body",
    "FileBody",
    "Header",
    "Path",
    "PydanticBody",
    "Query",
    "RapidApi",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "http",
]
