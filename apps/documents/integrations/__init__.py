

from .base import DocumentIntegration
from .capabilities import DocumentCapability
from .registry import (
    DocumentIntegrationRegistry,
    registry,
)
from .resolver import DocumentIntegrationResolver

__all__ = [
    "DocumentCapability",
    "DocumentIntegration",
    "DocumentIntegrationRegistry",
    "DocumentIntegrationResolver",
    "registry",
]