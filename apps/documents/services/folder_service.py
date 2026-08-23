

from __future__ import annotations

from django.db import transaction

from apps.documents.models import (
    DocumentFolder,
)
from apps.projects.models import Project


class DocumentFolderService:
    """
    Service de gestion de l'arborescence documentaire.

    Responsabilités :
    - créer un dossier ;
    - renommer un dossier ;
    - supprimer un dossier vide.

    Les opérations de déplacement et de copie
    seront ajoutées ultérieurement.
    """

    @staticmethod
    @transaction.atomic
    def create_folder(
        *,
        project: Project,
        name: str,
        parent: DocumentFolder | None = None,
    ) -> DocumentFolder:
        """
        Crée un dossier dans l'arborescence documentaire.
        """

        normalized_name = (
            DocumentFolderService._normalize_name(
                name
            )
        )

        if (
            parent is not None
            and parent.project_id != project.pk
        ):
            raise ValueError(
                "Le dossier parent doit appartenir "
                "au même projet."
            )

        if (
            DocumentFolder.objects
            .filter(
                project=project,
                parent=parent,
                name=normalized_name,
            )
            .exists()
        ):
            raise ValueError(
                "Un dossier portant ce nom existe "
                "déjà à cet emplacement."
            )

        folder = DocumentFolder(
            project=project,
            parent=parent,
            name=normalized_name,
        )

        folder.full_clean()
        folder.save()

        return folder

    @staticmethod
    @transaction.atomic
    def rename_folder(
        *,
        folder: DocumentFolder,
        name: str,
    ) -> DocumentFolder:
        """
        Renomme un dossier.
        """

        normalized_name = (
            DocumentFolderService._normalize_name(
                name
            )
        )

        if normalized_name == folder.name:
            return folder

        if (
            DocumentFolder.objects
            .filter(
                project=folder.project,
                parent=folder.parent,
                name=normalized_name,
            )
            .exclude(
                pk=folder.pk,
            )
            .exists()
        ):
            raise ValueError(
                "Un dossier portant ce nom existe "
                "déjà à cet emplacement."
            )

        folder.name = normalized_name

        folder.full_clean()
        folder.save(
            update_fields=[
                "name",
                "updated_at",
            ]
        )

        return folder

    @staticmethod
    @transaction.atomic
    def delete_folder(
        *,
        folder: DocumentFolder,
    ) -> None:
        """
        Supprime définitivement un dossier vide.

        Un dossier contenant des sous-dossiers ou
        des documents ne peut pas être supprimé.
        """

        if folder.children.exists():
            raise ValueError(
                "Le dossier contient des "
                "sous-dossiers."
            )

        if folder.documents.exists():
            raise ValueError(
                "Le dossier contient des documents."
            )

        folder.delete()

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:
        """
        Normalise et valide un nom de dossier.
        """

        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Le nom du dossier ne peut pas "
                "être vide."
            )

        if normalized_name in {
            ".",
            "..",
        }:
            raise ValueError(
                "Nom de dossier invalide."
            )

        return normalized_name