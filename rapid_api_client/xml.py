"""
XML support module for rapid-api-client.

This module provides utilities for working with Pydantic XML models,
including checking for the pydantic-xml dependency and default transformation
functions for XML serialization.
"""

from functools import partial
from typing import Any, Callable, Optional

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore


def check_pydantic_xml_installed():
    """
    Ensure pydantic-xml package has been installed to use XML model pydantic classes.

    Raises:
        AssertionError: If pydantic-xml is not installed.
    """
    assert pydantic_xml, "pydantic-xml must be installed to use XML serialization"


pydantic_xml_transformer: Optional[Callable[[Any], Any]] = (
    partial(pydantic_xml.BaseXmlModel.to_xml, exclude_none=True)
    if pydantic_xml
    else None
)
