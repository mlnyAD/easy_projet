

from __future__ import annotations

from django.conf import settings

from .base import DocumentStorage
from .filesystem import FileSystemDocumentStorage


def get_document_storage() -> DocumentStorage:
    """
    Retourne le stockage documentaire configuré pour Easy Projet.

    La V1 utilise le système de fichiers local.
    """

    return FileSystemDocumentStorage(
        root=settings.DOCUMENT_STORAGE_ROOT
    )