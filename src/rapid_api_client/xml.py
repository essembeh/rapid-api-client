"""
XML support module for rapid-api-client.

This module provides utilities for working with Pydantic XML models,
including checking for the pydantic-xml dependency and default transformation
functions for XML serialization.
"""

from collections.abc import Callable
from functools import partial
from typing import Any

try:
    import pydantic_xml
except ImportError:  # pragma: nocover
    pydantic_xml = None  # type: ignore

# `pydantic_xml` is re-exported: client.py imports the guarded symbol from here
# so the optional-dependency handling stays in a single place.
__all__ = ["check_pydantic_xml_installed", "pydantic_xml", "pydantic_xml_transformer"]


def check_pydantic_xml_installed() -> None:
    """
    Ensure pydantic-xml package has been installed to use XML model pydantic classes.

    Raises:
        ImportError: If pydantic-xml is not installed.
    """
    if pydantic_xml is None:
        raise ImportError("pydantic-xml must be installed to use XML serialization")


pydantic_xml_transformer: Callable[[Any], Any] | None = (
    partial(pydantic_xml.BaseXmlModel.to_xml, exclude_none=True) if pydantic_xml else None
)
