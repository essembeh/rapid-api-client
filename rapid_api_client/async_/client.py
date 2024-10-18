from dataclasses import dataclass, field

from httpx import AsyncClient

from ..client import RapidApi


@dataclass
class AsyncRapidApi(RapidApi[AsyncClient]):
    client: AsyncClient = field(default_factory=AsyncClient)
