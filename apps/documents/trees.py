

from __future__ import annotations

from collections.abc import Sequence
from urllib.parse import urlencode

from django.urls import reverse

from apps.documents.models import DocumentFolder
from apps.projects.models import Project
from framework.runtime import TreeNode
from framework.tree import (
    TreeCommandDefinition,
    TreeCommandTarget,
    TreeDefinition,
    TreeNodeKind,
    TreeWorkspaceDefinition,
)


DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER = "documentation"
DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER = "doe"


DOCUMENT_EXPLORER_CREATE_ROOT_FOLDER_COMMAND = (
    TreeCommandDefinition(
        identifier="create-root-folder",
        label="Insérer un répertoire",
        icon="folder-plus",
        target=TreeCommandTarget.WORKSPACE,
        order=10,
    )
)


DOCUMENT_EXPLORER_GENERATE_DOE_COMMAND = (
    TreeCommandDefinition(
        identifier="generate-doe",
        label="Générer le DOE",
        icon="archive",
        target=TreeCommandTarget.WORKSPACE,
        order=10,
    )
)


DOCUMENT_EXPLORER_REFRESH_DOE_COMMAND = (
    TreeCommandDefinition(
        identifier="refresh-doe",
        label="Rafraîchir le DOE",
        icon="refresh-cw",
        target=TreeCommandTarget.WORKSPACE,
        order=10,
    )
)


DOCUMENT_EXPLORER_DOWNLOAD_DOE_COMMAND = (
    TreeCommandDefinition(
        identifier="download-doe",
        label="Télécharger le DOE",
        icon="download",
        target=TreeCommandTarget.WORKSPACE,
        order=20,
    )
)


DOCUMENT_EXPLORER_TREE_DEFINITION = TreeDefinition(
    identifier="document-explorer",
    workspaces=(
        TreeWorkspaceDefinition(
            identifier=DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER,
            label="Documentation",
            icon="folder-tree",
            commands=(
                DOCUMENT_EXPLORER_CREATE_ROOT_FOLDER_COMMAND,
            ),
        ),
        TreeWorkspaceDefinition(
            identifier=DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER,
            label="DOE",
            icon="archive",
            commands=(
                DOCUMENT_EXPLORER_GENERATE_DOE_COMMAND,
                DOCUMENT_EXPLORER_REFRESH_DOE_COMMAND,
                DOCUMENT_EXPLORER_DOWNLOAD_DOE_COMMAND,
            ),
        ),
    ),
)


class DocumentFolderTreeNodeFactory:
    """
    Adapte les dossiers documentaires au composant générique
    d'arborescence.
    """

    @classmethod
    def build(
        cls,
        *,
        project: Project,
        folders: Sequence[DocumentFolder],
        selected_folder_id: object | None,
        return_url: str,
        workspace_identifier: str = (
            DOCUMENT_EXPLORER_WORKSPACE_IDENTIFIER
        ),
    ) -> tuple[TreeNode, ...]:
        return tuple(
            cls._build_node(
                project=project,
                folder=folder,
                selected_folder_id=selected_folder_id,
                return_url=return_url,
                workspace_identifier=workspace_identifier,
            )
            for folder in folders
        )

    @staticmethod
    def _build_node(
        *,
        project: Project,
        folder: DocumentFolder,
        selected_folder_id: object | None,
        return_url: str,
        workspace_identifier: str,
    ) -> TreeNode:
        folder_url = reverse(
            "documents:folder",
            kwargs={
                "project_id": project.pk,
                "folder_id": folder.pk,
            },
        )

        if (
            workspace_identifier
            == DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER
        ):
            folder_url = (
                f"{folder_url}?"
                f"{urlencode({'workspace': workspace_identifier})}"
            )

        doe_selection_url = reverse(
            "documents:folder-doe-selection",
            kwargs={
                "project_id": project.pk,
                "folder_id": folder.pk,
            },
        )

        return TreeNode(
            identifier=str(folder.pk),
            parent_identifier=(
                str(folder.parent_id)
                if folder.parent_id is not None
                else None
            ),
            label=folder.name,
            kind=TreeNodeKind.BRANCH,
            source_object=folder,
            icon=(
                "folder-open"
                if folder.pk == selected_folder_id
                else "folder"
            ),
            url=folder_url,
            data_attributes={
                "folder-context": "",
                "folder-id": str(folder.pk),
                "folder-name": folder.name,
                "folder-create-url": reverse(
                    "documents:folder-create",
                    kwargs={
                        "project_id": project.pk,
                    },
                ),
                "folder-rename-url": reverse(
                    "documents:folder-rename",
                    kwargs={
                        "project_id": project.pk,
                        "folder_id": folder.pk,
                    },
                ),
                "folder-delete-url": reverse(
                    "documents:folder-delete",
                    kwargs={
                        "project_id": project.pk,
                        "folder_id": folder.pk,
                    },
                ),
                "folder-move-url": reverse(
                    "documents:folder-move",
                    kwargs={
                        "project_id": project.pk,
                        "folder_id": folder.pk,
                    },
                ),
                "folder-doe-url": (
                    f"{doe_selection_url}?"
                    f"{urlencode({'next': return_url})}"
                ),
                "folder-is-doe": (
                    "true"
                    if folder.is_doe
                    else "false"
                ),
                "folder-doe-protected": (
                    "true"
                    if (
                        folder.is_doe_root
                        or folder.is_doe_generated
                    )
                    else "false"
                ),
            },
        )