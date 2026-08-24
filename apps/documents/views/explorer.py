

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.documents.models import (
    Document,
    DocumentFavorite,
    DocumentFolder,
)
from apps.projects.models import Project


class DocumentExplorerView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Explorateur documentaire d'un projet.

    Le dossier courant est facultatif :
    - sans folder_id : racine documentaire du projet ;
    - avec folder_id : contenu du dossier sélectionné.
    """

    template_name = (
        "documents/document_explorer.html"
    )

    def get_project(self) -> Project:
        return get_object_or_404(
            Project.objects.select_related(
                "company",
            ),
            pk=self.kwargs["project_id"],
        )

    def get_current_folder(
        self,
        project: Project,
    ) -> DocumentFolder | None:
        folder_id = self.kwargs.get(
            "folder_id"
        )

        if folder_id is None:
            return None

        return get_object_or_404(
            DocumentFolder.objects.select_related(
                "parent",
            ),
            pk=folder_id,
            project=project,
            is_active=True,
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        project = self.get_project()

        current_folder = (
            self.get_current_folder(
                project
            )
        )

        destination_folders = (
            DocumentFolder.objects
            .filter(
                project=project,
                is_active=True,
            )
            .select_related(
                "parent",
            )
            .order_by(
                "name",
            )
        )

        # --------------------------------------------------------------
        # Racines visibles dans l'arbre gauche
        # --------------------------------------------------------------

        root_folders = (
            DocumentFolder.objects
            .filter(
                project=project,
                parent__isnull=True,
                is_active=True,
            )
            .prefetch_related(
                "children",
            )
            .order_by(
                "sort_order",
                "name",
            )
        )

        open_folder_ids = set()

        current = current_folder

        while current is not None:
            open_folder_ids.add(
                current.pk
            )
            current = current.parent

        # --------------------------------------------------------------
        # Contenu du panneau droit
        # --------------------------------------------------------------

        favorite_document_ids = set()

        if current_folder is None:
            child_folders = root_folders
            documents = Document.objects.none()

        else:
            child_folders = (
                DocumentFolder.objects
                .filter(
                    project=project,
                    parent=current_folder,
                    is_active=True,
                )
                .order_by(
                    "sort_order",
                    "name",
                )
            )

            documents = (
                Document.objects
                .filter(
                    project=project,
                    folder=current_folder,
                )
                .select_related(
                    "document_type",
                    "status",
                    "lifecycle",
                    "current_version",
                )
                .order_by(
                    "title"
                )
            )

            favorite_document_ids = set(
                DocumentFavorite.objects
                .filter(
                    user=self.request.user,
                    document__in=documents,
                )
                .values_list(
                    "document_id",
                    flat=True,
                )
            )

        context.update(
            {
                "project": project,
                "current_folder": current_folder,
                "root_folders": root_folders,
                "child_folders": child_folders,
                "documents": documents,
                "breadcrumbs": (
                    self.build_breadcrumbs(
                        current_folder
                    )
                ),
                "open_folder_ids": open_folder_ids,
                "destination_folders": (
                    destination_folders
                ),
                "favorite_document_ids": (
                    favorite_document_ids
                ),
            }
        )

        return context

    @staticmethod
    def build_breadcrumbs(
        folder: DocumentFolder | None,
    ) -> list[DocumentFolder]:
        """
        Construit le chemin racine -> dossier courant.
        """

        if folder is None:
            return []

        breadcrumbs = []

        current = folder

        while current is not None:
            breadcrumbs.append(
                current
            )
            current = current.parent

        breadcrumbs.reverse()

        return breadcrumbs