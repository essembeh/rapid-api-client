"""
rapid-api-client
"""

from importlib.metadata import version

from .annotations import Body as Body
from .annotations import FileBody as FileBody
from .annotations import FormBody as FormBody
from .annotations import Header as Header
from .annotations import Path as Path
from .annotations import PydanticBody as PydanticBody
from .annotations import PydanticXmlBody as PydanticXmlBody
from .annotations import Query as Query
from .client import RapidApi as RapidApi
from .decorator import delete as delete
from .decorator import get as get
from .decorator import http as http
from .decorator import patch as patch
from .decorator import post as post
from .decorator import put as put

__version__ = version(__name__)
