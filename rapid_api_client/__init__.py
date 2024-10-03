"""
rapid-api-client
"""

from importlib.metadata import version

from .client import delete, get, http, patch, post, put
from .model import Body, FileBody, Header, Path, PydanticBody, Query, RapidApi

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
