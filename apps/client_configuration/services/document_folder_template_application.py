

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction

from apps.documents.models import DocumentFolder
from apps.documents.services.folder_service import (
    DocumentFolderService,
)

from ..models import (
    DocumentFolderTemplate,
    DocumentFolderTemplateFolder,
)

if TYPE_CHECKING:
    from apps.projects.models import Project


class DocumentFolderTemplateApplicationService:
    """
    Applique au projet l'arborescence documentaire par défaut
    de son environnement client.
    """

    @classmethod
    @transaction.atomic
    def apply_default_template(
        cls,
        *,
        project: Project,
    ) -> int:
        """
        Copie l'arborescence par défaut dans le projet.

        Retourne le nombre de dossiers créés.
        Aucun dossier n'est créé lorsqu'aucun modèle actif
        n'est défini par défaut.
        """

        if project.client_environment_id is None:
            raise ValueError(
                "Le projet doit appartenir à un environnement client."
            )

        if DocumentFolder.objects.filter(
            project=project,
        ).exists():
            raise ValueError(
                "L'arborescence documentaire du projet existe déjà."
            )

        template = (
            DocumentFolderTemplate.objects
            .filter(
                client_environment_id=(
                    project.client_environment_id
                ),
                is_active=True,
                is_default=True,
            )
            .first()
        )

        if template is None:
            return 0

        root_folders = (
            DocumentFolderTemplateFolder.objects
            .filter(
                template=template,
                parent__isnull=True,
                is_active=True,
            )
            .order_by(
                "sort_order",
                "name",
            )
        )

        return cls._copy_folders(
            project=project,
            template_folders=root_folders,
            parent=None,
        )

    @classmethod
    def _copy_folders(
        cls,
        *,
        project: Project,
        template_folders,
        parent: DocumentFolder | None,
    ) -> int:
        """
        Copie récursivement les dossiers actifs du modèle.
        """

        created_count = 0

        for template_folder in template_folders:
            folder = DocumentFolderService.create_folder(
                project=project,
                parent=parent,
                name=template_folder.name,
            )

            if folder.sort_order != template_folder.sort_order:
                folder.sort_order = template_folder.sort_order
                folder.save(
                    update_fields=[
                        "sort_order",
                        "updated_at",
                    ]
                )

            created_count += 1

            child_folders = (
                template_folder.children
                .filter(
                    is_active=True,
                )
                .order_by(
                    "sort_order",
                    "name",
                )
            )

            created_count += cls._copy_folders(
                project=project,
                template_folders=child_folders,
                parent=folder,
            )

        return created_count
    