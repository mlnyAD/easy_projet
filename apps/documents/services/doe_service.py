

from __future__ import annotations

from django.db import transaction

from apps.documents.models import (
    Document,
    DocumentFolder,
    DoeGeneration,
)
from apps.documents.services.document_service import (
    DocumentService,
)
from apps.projects.models import Project
from apps.users.models import User


class DoeService:
    """
    Construit et rafraîchit le DOE d'un projet.

    Le DOE est une copie structurée des documents sélectionnés.
    Les originaux et leur arborescence restent inchangés.
    """

    ROOT_FOLDER_NAME = "DOE"

    def __init__(
        self,
        document_service: DocumentService | None = None,
    ) -> None:
        self.document_service = (
            document_service
            or DocumentService()
        )

    @transaction.atomic
    def generate(
        self,
        *,
        project: Project,
        user: User,
    ) -> DoeGeneration | None:
        """
        Génère ou rafraîchit le DOE du projet.

        Retourne None lorsqu'aucun document source n'est sélectionné.
        """

        source_folders = {
            folder.pk: folder
            for folder in (
                DocumentFolder.objects
                .filter(
                    project=project,
                    is_active=True,
                    is_doe_root=False,
                    is_doe_generated=False,
                )
                .order_by(
                    "sort_order",
                    "name",
                )
            )
        }

        selected_folder_ids = {
            folder.pk
            for folder in source_folders.values()
            if folder.is_doe
        }

        source_documents = self._get_selected_documents(
            project=project,
            source_folders=source_folders,
            selected_folder_ids=selected_folder_ids,
        )

        if not source_documents:
            return None

        doe_root = self._get_or_create_root_folder(
            project=project,
        )

        self._clear_previous_generation(
            project=project,
        )

        destination_folders: dict[
            object,
            DocumentFolder,
        ] = {}

        for source_document in source_documents:
            destination = self._get_destination_folder(
                source_folder=source_document.folder,
                doe_root=doe_root,
                source_folders=source_folders,
                destination_folders=destination_folders,
            )

            self.document_service.copy_document(
                document=source_document,
                destination=destination,
                user=user,
                is_doe=False,
                is_doe_generated=True,
                doe_source_document=source_document,
            )

        return DoeGeneration.objects.create(
            project=project,
            doe_root_folder=doe_root,
            generated_by=user,
            document_count=len(source_documents),
        )

    def _get_selected_documents(
        self,
        *,
        project: Project,
        source_folders: dict[object, DocumentFolder],
        selected_folder_ids: set[object],
    ) -> list[Document]:
        """
        Retourne les documents explicitement sélectionnés ou inclus
        par un dossier source sélectionné.
        """

        documents = (
            Document.objects
            .filter(
                project=project,
                is_doe_generated=False,
                current_version__isnull=False,
                folder__is_doe_root=False,
                folder__is_doe_generated=False,
            )
            .select_related(
                "folder",
                "current_version",
                "document_type",
                "status",
                "lifecycle",
            )
            .order_by(
                "folder__sort_order",
                "folder__name",
                "title",
            )
        )

        return [
            document
            for document in documents
            if (
                document.is_doe
                or self._folder_is_selected(
                    folder_id=document.folder_id,
                    source_folders=source_folders,
                    selected_folder_ids=selected_folder_ids,
                )
            )
        ]

    @staticmethod
    def _folder_is_selected(
        *,
        folder_id,
        source_folders: dict[object, DocumentFolder],
        selected_folder_ids: set[object],
    ) -> bool:
        """
        Indique si un dossier ou l'un de ses parents est sélectionné.
        """

        current_id = folder_id

        while current_id is not None:
            if current_id in selected_folder_ids:
                return True

            current = source_folders.get(current_id)

            if current is None:
                return False

            current_id = current.parent_id

        return False

    def _get_or_create_root_folder(
        self,
        *,
        project: Project,
    ) -> DocumentFolder:
        """
        Retourne la racine DOE du projet ou la crée.
        """

        existing_root = (
            DocumentFolder.objects
            .filter(
                project=project,
                is_doe_root=True,
            )
            .first()
        )

        if existing_root is not None:
            return existing_root

        conflicting_folder = (
            DocumentFolder.objects
            .filter(
                project=project,
                parent__isnull=True,
                name=self.ROOT_FOLDER_NAME,
            )
            .first()
        )

        if conflicting_folder is not None:
            raise ValueError(
                'Un dossier racine nommé "DOE" existe déjà '
                "sans être identifié comme dossier DOE."
            )

        doe_root = DocumentFolder(
            project=project,
            name=self.ROOT_FOLDER_NAME,
            is_doe_root=True,
        )

        doe_root.full_clean()
        doe_root.save()

        return doe_root

    def _clear_previous_generation(
        self,
        *,
        project: Project,
    ) -> None:
        """
        Supprime les copies et dossiers issus de la génération
        précédente, sans jamais supprimer les originaux.
        """

        generated_documents = list(
            Document.objects
            .filter(
                project=project,
                is_doe_generated=True,
            )
            .select_related("current_version")
        )

        for document in generated_documents:
            self.document_service.delete_document(
                document=document,
            )

        (
            DocumentFolder.objects
            .filter(
                project=project,
                is_doe_generated=True,
            )
            .delete()
        )

    def _get_destination_folder(
        self,
        *,
        source_folder: DocumentFolder,
        doe_root: DocumentFolder,
        source_folders: dict[object, DocumentFolder],
        destination_folders: dict[object, DocumentFolder],
    ) -> DocumentFolder:
        """
        Crée, si nécessaire, le chemin miroir du dossier source
        sous la racine DOE.
        """

        cached_destination = destination_folders.get(
            source_folder.pk
        )

        if cached_destination is not None:
            return cached_destination

        if source_folder.parent_id is None:
            destination_parent = doe_root
        else:
            source_parent = source_folders[
                source_folder.parent_id
            ]

            destination_parent = self._get_destination_folder(
                source_folder=source_parent,
                doe_root=doe_root,
                source_folders=source_folders,
                destination_folders=destination_folders,
            )

        destination = DocumentFolder(
            project=doe_root.project,
            parent=destination_parent,
            name=source_folder.name,
            sort_order=source_folder.sort_order,
            is_doe_generated=True,
        )

        destination.full_clean()
        destination.save()

        destination_folders[source_folder.pk] = destination

        return destination