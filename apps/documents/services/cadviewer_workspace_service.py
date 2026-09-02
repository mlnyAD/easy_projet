

from __future__ import annotations

from pathlib import Path
from shutil import copyfileobj

from django.conf import settings

from apps.documents.models import DocumentVersion
from apps.documents.storage import get_document_storage


class CadViewerWorkspaceService:
    """
    Prépare une DocumentVersion pour CADViewer.

    Easy Projet reste propriétaire du fichier source.

    Le fichier copié dans l'espace CADViewer est uniquement
    un fichier de travail destiné à la visualisation.
    """

    @classmethod
    def prepare_version(
        cls,
        *,
        version: DocumentVersion,
    ) -> str:
        """
        Copie la version documentaire dans l'espace partagé
        avec CADViewer puis retourne son URL publique.
        """

        workspace_path = cls._get_workspace_path()

        workspace_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = (
            Path(
                version.original_filename
            )
            .suffix
            .lower()
        )

        filename = (
            f"{version.pk}"
            f"{extension}"
        )

        destination = (
            workspace_path
            / filename
        )

        storage = get_document_storage()

        if not storage.exists(
            version.storage_key
        ):
            raise FileNotFoundError(
                "Fichier documentaire introuvable."
            )

        with storage.open(
            version.storage_key
        ) as source:
            with destination.open(
                "wb"
            ) as target:
                copyfileobj(
                    source,
                    target,
                )

        cadviewer_url = (
            settings.CADVIEWER_URL
            .strip()
            .rstrip("/")
        )

        if not cadviewer_url:
            raise RuntimeError(
                "CADVIEWER_URL n'est pas configurée."
            )

        return (
            f"{cadviewer_url}"
            f"/content/drawings/dwg/easy_projet/"
            f"{filename}"
        )

    @staticmethod
    def _get_workspace_path() -> Path:
        """
        Retourne le répertoire local partagé avec CADViewer.
        """

        configured_path = (
            settings.CADVIEWER_WORKSPACE_PATH
            .strip()
        )

        if not configured_path:
            raise RuntimeError(
                "CADVIEWER_WORKSPACE_PATH "
                "n'est pas configuré."
            )

        return Path(
            configured_path
        )