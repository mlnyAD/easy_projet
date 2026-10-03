

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView

from apps.documents.models import (
    Document,
    DocumentFavorite,
    DocumentFolder,
)
from apps.documents.trees import (
    DOCUMENT_EXPLORER_CREATE_ROOT_FOLDER_COMMAND,
    DOCUMENT_EXPLORER_TREE_DEFINITION,
    DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER,
    DocumentFolderTreeNodeFactory,
)
from apps.projects.models import Project
from apps.projects.services.access import (
    ProjectAccessService,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
from framework.runtime import EPTree, TreeCommand
from framework.viewmodel import TreeViewModelBuilder


class DocumentExplorerView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Explorateur documentaire d'un projet.
    """

    template_name = (
        "documents/document_explorer.html"
    )

    def get_project(self) -> Project:
        return get_object_or_404(
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
            .select_related(
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

    def get_regular_folders(
        self,
        project: Project,
    ):
        """
        Retourne les dossiers de la documentation source.

        Les dossiers générés pour le DOE ne font pas partie de
        l'environnement documentaire courant.
        """

        return (
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

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        project = self.get_project()

        current_folder = self.get_current_folder(
            project
        )

        can_work_on_project = (
            ProjectAuthorizationService
            .can_work_on_project(
                user=self.request.user,
                project=project,
            )
        )

        regular_folders = tuple(
            self.get_regular_folders(project)
        )

        root_folders = tuple(
            folder
            for folder in regular_folders
            if folder.parent_id is None
        )

        destination_folders = regular_folders

        open_folder_ids = set()

        current = current_folder

        while current is not None:
            open_folder_ids.add(
                current.pk
            )
            current = current.parent

        favorite_document_ids = set()

        if current_folder is None:
            child_folders = root_folders
            documents = Document.objects.none()
        else:
            child_folders = tuple(
                folder
                for folder in regular_folders
                if folder.parent_id == current_folder.pk
            )

            documents = (
                Document.objects
                .filter(
                    project=project,
                    folder=current_folder,
                    is_doe_generated=False,
                )
                .select_related(
                    "document_type",
                    "status",
                    "lifecycle",
                    "current_version",
                )
                .order_by(
                    "title",
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

        return_url = self.request.get_full_path()

        tree_nodes = DocumentFolderTreeNodeFactory.build(
            project=project,
            folders=regular_folders,
            selected_folder_id=(
                current_folder.pk
                if current_folder is not None
                else None
            ),
            return_url=return_url,
        )

        tree_commands = ()

        if can_work_on_project:
            tree_commands = (
                TreeCommand(
                    definition=(
                        DOCUMENT_EXPLORER_CREATE_ROOT_FOLDER_COMMAND
                    ),
                ),
            )

        tree_runtime = EPTree(
            definition=DOCUMENT_EXPLORER_TREE_DEFINITION,
            workspace_identifier=(
                DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER
            ),
            nodes=tree_nodes,
            commands=tree_commands,
            selected_node_identifier=(
                str(current_folder.pk)
                if current_folder is not None
                else None
            ),
        )

        tree_view = TreeViewModelBuilder().build(
            runtime=tree_runtime,
            expanded_node_identifiers=tuple(
                str(folder_id)
                for folder_id in open_folder_ids
                if (
                    current_folder is None
                    or folder_id != current_folder.pk
                )
            ),
            workspace_urls={
                DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER: reverse(
                    "documents:explorer",
                    kwargs={
                        "project_id": project.pk,
                    },
                ),
            },
        )

        context.update(
            {
                "project": project,
                "current_folder": current_folder,
                "root_folders": root_folders,
                "child_folders": child_folders,
                "documents": documents,
                "breadcrumbs": self.build_breadcrumbs(
                    current_folder
                ),
                "open_folder_ids": open_folder_ids,
                "destination_folders": (
                    destination_folders
                ),
                "favorite_document_ids": (
                    favorite_document_ids
                ),
                "can_work_on_project": (
                    can_work_on_project
                ),
                "return_url": return_url,
                "tree_view": tree_view,
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