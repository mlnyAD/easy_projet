

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
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
    DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER,
    DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER,
    DOCUMENT_EXPLORER_DOWNLOAD_DOE_COMMAND,
    DOCUMENT_EXPLORER_GENERATE_DOE_COMMAND,
    DOCUMENT_EXPLORER_REFRESH_DOE_COMMAND,
    DOCUMENT_EXPLORER_TREE_DEFINITION,
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

    Deux environnements sont disponibles :
    - Documentation : dossiers et documents sources ;
    - DOE : copie générée en lecture seule.
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

    def get_workspace_identifier(self) -> str:
        workspace_identifier = (
            self.request.GET.get("workspace")
            or DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER
        )

        valid_identifiers = {
            DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER,
            DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER,
        }

        if workspace_identifier not in valid_identifiers:
            raise Http404(
                "Environnement documentaire introuvable."
            )

        return workspace_identifier

    def get_current_folder(
        self,
        *,
        project: Project,
        workspace_identifier: str,
    ) -> DocumentFolder | None:
        folder_id = self.kwargs.get(
            "folder_id"
        )

        if folder_id is None:
            return None

        queryset = (
            DocumentFolder.objects
            .select_related("parent")
            .filter(
                project=project,
                is_active=True,
            )
        )

        if (
            workspace_identifier
            == DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER
        ):
            queryset = queryset.filter(
                Q(is_doe_root=True)
                | Q(is_doe_generated=True)
            )
        else:
            queryset = queryset.filter(
                is_doe_root=False,
                is_doe_generated=False,
            )

        return get_object_or_404(
            queryset,
            pk=folder_id,
        )

    def get_workspace_folders(
        self,
        *,
        project: Project,
        workspace_identifier: str,
    ):
        queryset = (
            DocumentFolder.objects
            .filter(
                project=project,
                is_active=True,
            )
            .order_by(
                "sort_order",
                "name",
            )
        )

        if (
            workspace_identifier
            == DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER
        ):
            return queryset.filter(
                Q(is_doe_root=True)
                | Q(is_doe_generated=True)
            )

        return queryset.filter(
            is_doe_root=False,
            is_doe_generated=False,
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        project = self.get_project()

        workspace_identifier = (
            self.get_workspace_identifier()
        )

        is_doe_workspace = (
            workspace_identifier
            == DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER
        )

        current_folder = self.get_current_folder(
            project=project,
            workspace_identifier=workspace_identifier,
        )

        can_work_on_project = (
            ProjectAuthorizationService
            .can_work_on_project(
                user=self.request.user,
                project=project,
            )
        )

        can_work_on_workspace = (
            can_work_on_project
            and not is_doe_workspace
        )

        workspace_folders = tuple(
            self.get_workspace_folders(
                project=project,
                workspace_identifier=workspace_identifier,
            )
        )

        root_folders = tuple(
            folder
            for folder in workspace_folders
            if folder.parent_id is None
        )

        if current_folder is None:
            child_folders = root_folders
            documents = Document.objects.none()
        else:
            child_folders = tuple(
                folder
                for folder in workspace_folders
                if folder.parent_id == current_folder.pk
            )

            documents = (
                Document.objects
                .filter(
                    project=project,
                    folder=current_folder,
                    is_doe_generated=is_doe_workspace,
                )
                .select_related(
                    "document_type",
                    "status",
                    "lifecycle",
                    "current_version",
                )
                .order_by("title")
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

        open_folder_ids = set()

        current = current_folder

        while current is not None:
            open_folder_ids.add(current.pk)
            current = current.parent

        return_url = self.request.get_full_path()

        tree_nodes = DocumentFolderTreeNodeFactory.build(
            project=project,
            folders=workspace_folders,
            selected_folder_id=(
                current_folder.pk
                if current_folder is not None
                else None
            ),
            return_url=return_url,
            workspace_identifier=workspace_identifier,
        )

        doe_root = next(
            (
                folder
                for folder in workspace_folders
                if folder.is_doe_root
            ),
            None,
        )

        tree_commands = self.get_tree_commands(
            project=project,
            workspace_identifier=workspace_identifier,
            can_work_on_project=can_work_on_project,
            doe_root=doe_root,
            return_url=return_url,
        )

        tree_runtime = EPTree(
            definition=DOCUMENT_EXPLORER_TREE_DEFINITION,
            workspace_identifier=workspace_identifier,
            nodes=tree_nodes,
            commands=tree_commands,
            selected_node_identifier=(
                str(current_folder.pk)
                if current_folder is not None
                else None
            ),
        )

        explorer_url = reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
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
                DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER: (
                    explorer_url
                ),
                DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER: (
                    f"{explorer_url}?"
                    f"{urlencode({'workspace': 'doe'})}"
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
                    workspace_folders
                    if can_work_on_workspace
                    else ()
                ),
                "favorite_document_ids": (
                    favorite_document_ids
                ),
                "can_work_on_project": (
                    can_work_on_workspace
                ),
                "return_url": return_url,
                "tree_view": tree_view,
                "is_doe_workspace": is_doe_workspace,
            }
        )

        return context

    @staticmethod
    def get_tree_commands(
        *,
        project: Project,
        workspace_identifier: str,
        can_work_on_project: bool,
        doe_root: DocumentFolder | None,
        return_url: str,
    ) -> tuple[TreeCommand, ...]:
        if (
            workspace_identifier
            == DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER
        ):
            if not can_work_on_project:
                return ()

            return (
                TreeCommand(
                    definition=(
                        DOCUMENT_EXPLORER_CREATE_ROOT_FOLDER_COMMAND
                    ),
                ),
            )

        explorer_url = reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )

        doe_workspace_url = (
            f"{explorer_url}?"
            f"{urlencode({'workspace': 'doe'})}"
        )

        commands: list[TreeCommand] = []

        if can_work_on_project:
            commands.append(
                TreeCommand(
                    definition=(
                        DOCUMENT_EXPLORER_REFRESH_DOE_COMMAND
                        if doe_root is not None
                        else DOCUMENT_EXPLORER_GENERATE_DOE_COMMAND
                    ),
                    url=(
                        f"{reverse(
                            'documents:doe-generate',
                            kwargs={
                                'project_id': project.pk,
                            },
                        )}?"
                        f"{urlencode({'next': doe_workspace_url})}"
                    ),
                    method="POST",
                )
            )

        if doe_root is not None:
            commands.append(
                TreeCommand(
                    definition=(
                        DOCUMENT_EXPLORER_DOWNLOAD_DOE_COMMAND
                    ),
                    url=reverse(
                        "documents:folder-download",
                        kwargs={
                            "project_id": project.pk,
                            "folder_id": doe_root.pk,
                        },
                    ),
                )
            )

        return tuple(commands)

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
            breadcrumbs.append(current)
            current = current.parent

        breadcrumbs.reverse()

        return breadcrumbs