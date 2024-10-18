from typing import TypeVar

from httpx._client import BaseClient
from pydantic import BaseModel

from .annotations import BaseAnnotation

BA = TypeVar("BA", bound=BaseAnnotation)
BM = TypeVar("BM", bound=BaseModel)
T = TypeVar("T")
CLIENT = TypeVar("CLIENT", bound=BaseClient)
