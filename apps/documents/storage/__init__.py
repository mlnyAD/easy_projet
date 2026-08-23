

from .base import DocumentStorage
from .factory import get_document_storage
from .filesystem import FileSystemDocumentStorage

__all__ = [
    "DocumentStorage",
    "FileSystemDocumentStorage",
    "get_document_storage",
]