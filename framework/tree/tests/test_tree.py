

from __future__ import annotations

import unittest

from framework.runtime import EPTree, TreeCommand, TreeNode
from framework.tree import (
    TreeCommandDefinition,
    TreeCommandTarget,
    TreeDefinition,
    TreeNodeKind,
    TreeWorkspaceDefinition,
)
from framework.viewmodel import TreeViewModelBuilder


class TreeDefinitionTests(unittest.TestCase):
    """
    Vérifie les définitions statiques de l'arborescence.
    """

    def test_definition_exposes_workspaces(self) -> None:
        documentation = TreeWorkspaceDefinition(
            identifier="documentation",
            label="Documentation",
            icon="folder-open",
        )
        doe = TreeWorkspaceDefinition(
            identifier="doe",
            label="DOE",
            icon="folder-archive",
        )

        definition = TreeDefinition(
            identifier="project-documents",
            workspaces=(
                documentation,
                doe,
            ),
        )

        self.assertEqual(
            definition.identifier,
            "project-documents",
        )
        self.assertTrue(
            definition.has_workspace("documentation")
        )
        self.assertEqual(
            definition.get_workspace("doe"),
            doe,
        )
        self.assertEqual(
            len(definition),
            2,
        )

    def test_definition_rejects_duplicate_workspace_identifier(
        self,
    ) -> None:
        workspace = TreeWorkspaceDefinition(
            identifier="documentation",
            label="Documentation",
            icon="folder-open",
        )

        with self.assertRaisesRegex(
            ValueError,
            "plusieurs fois",
        ):
            TreeDefinition(
                identifier="project-documents",
                workspaces=(
                    workspace,
                    TreeWorkspaceDefinition(
                        identifier="documentation",
                        label="Autre documentation",
                        icon="folder",
                    ),
                ),
            )

    def test_workspace_orders_commands(self) -> None:
        workspace = TreeWorkspaceDefinition(
            identifier="documentation",
            label="Documentation",
            icon="folder-open",
            commands=(
                TreeCommandDefinition(
                    identifier="download",
                    label="Télécharger",
                    icon="download",
                    target=TreeCommandTarget.SELECTION,
                    allowed_node_kinds=(
                        TreeNodeKind.BRANCH,
                    ),
                    order=20,
                ),
                TreeCommandDefinition(
                    identifier="import",
                    label="Importer",
                    icon="upload",
                    target=TreeCommandTarget.WORKSPACE,
                    order=10,
                ),
            ),
        )

        self.assertEqual(
            tuple(
                command.identifier
                for command in workspace.commands
            ),
            (
                "import",
                "download",
            ),
        )

    def test_workspace_command_rejects_node_kind_for_workspace(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "espace de travail",
        ):
            TreeCommandDefinition(
                identifier="invalid",
                label="Invalide",
                icon="x",
                target=TreeCommandTarget.WORKSPACE,
                allowed_node_kinds=(
                    TreeNodeKind.BRANCH,
                ),
            )


class EPTreeTests(unittest.TestCase):
    """
    Vérifie le runtime de l'arborescence.
    """

    def setUp(self) -> None:
        self.import_command_definition = (
            TreeCommandDefinition(
                identifier="import",
                label="Importer",
                icon="upload",
                target=TreeCommandTarget.WORKSPACE,
            )
        )

        self.download_command_definition = (
            TreeCommandDefinition(
                identifier="download",
                label="Télécharger",
                icon="download",
                target=TreeCommandTarget.SELECTION,
                allowed_node_kinds=(
                    TreeNodeKind.BRANCH,
                ),
            )
        )

        self.documentation_workspace = (
            TreeWorkspaceDefinition(
                identifier="documentation",
                label="Documentation",
                icon="folder-open",
                commands=(
                    self.import_command_definition,
                    self.download_command_definition,
                ),
            )
        )

        self.doe_workspace = TreeWorkspaceDefinition(
            identifier="doe",
            label="DOE",
            icon="folder-archive",
        )

        self.definition = TreeDefinition(
            identifier="project-documents",
            workspaces=(
                self.documentation_workspace,
                self.doe_workspace,
            ),
        )

    def test_runtime_exposes_hierarchy_and_selection(
        self,
    ) -> None:
        root = TreeNode(
            identifier="folder-plans",
            parent_identifier=None,
            label="Plans",
            kind=TreeNodeKind.BRANCH,
            source_object=object(),
            icon="folder",
        )
        child = TreeNode(
            identifier="document-plan-rdc",
            parent_identifier="folder-plans",
            label="Plan RDC",
            kind=TreeNodeKind.LEAF,
            source_object=object(),
            icon="file",
        )

        runtime = EPTree(
            definition=self.definition,
            workspace_identifier="documentation",
            nodes=(
                root,
                child,
            ),
            selected_node_identifier="document-plan-rdc",
        )

        self.assertEqual(
            runtime.workspace,
            self.documentation_workspace,
        )
        self.assertEqual(
            runtime.root_nodes,
            (root,),
        )
        self.assertEqual(
            runtime.get_children("folder-plans"),
            (child,),
        )
        self.assertEqual(
            runtime.selected_node,
            child,
        )

    def test_runtime_rejects_missing_parent(self) -> None:
        orphan = TreeNode(
            identifier="orphan",
            parent_identifier="missing",
            label="Orphelin",
            kind=TreeNodeKind.LEAF,
            source_object=object(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "n'existe pas",
        ):
            EPTree(
                definition=self.definition,
                workspace_identifier="documentation",
                nodes=(orphan,),
            )

    def test_runtime_rejects_leaf_parent(self) -> None:
        document = TreeNode(
            identifier="document",
            parent_identifier=None,
            label="Document",
            kind=TreeNodeKind.LEAF,
            source_object=object(),
        )
        child = TreeNode(
            identifier="child",
            parent_identifier="document",
            label="Enfant invalide",
            kind=TreeNodeKind.LEAF,
            source_object=object(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "BRANCH",
        ):
            EPTree(
                definition=self.definition,
                workspace_identifier="documentation",
                nodes=(
                    document,
                    child,
                ),
            )

    def test_runtime_rejects_unknown_workspace_command(
        self,
    ) -> None:
        unknown_command = TreeCommand(
            definition=TreeCommandDefinition(
                identifier="unknown",
                label="Inconnue",
                icon="circle-help",
                target=TreeCommandTarget.WORKSPACE,
            ),
            url="/unknown/",
        )

        with self.assertRaisesRegex(
            ValueError,
            "n'est pas déclarée",
        ):
            EPTree(
                definition=self.definition,
                workspace_identifier="documentation",
                nodes=(),
                commands=(unknown_command,),
            )


class TreeViewModelBuilderTests(unittest.TestCase):
    """
    Vérifie la transformation runtime vers présentation.
    """

    def setUp(self) -> None:
        self.import_command_definition = (
            TreeCommandDefinition(
                identifier="import",
                label="Importer",
                icon="upload",
                target=TreeCommandTarget.WORKSPACE,
                order=10,
            )
        )

        self.download_command_definition = (
            TreeCommandDefinition(
                identifier="download",
                label="Télécharger",
                icon="download",
                target=TreeCommandTarget.SELECTION,
                allowed_node_kinds=(
                    TreeNodeKind.BRANCH,
                ),
                order=20,
            )
        )

        documentation_workspace = TreeWorkspaceDefinition(
            identifier="documentation",
            label="Documentation",
            icon="folder-open",
            commands=(
                self.import_command_definition,
                self.download_command_definition,
            ),
        )

        doe_workspace = TreeWorkspaceDefinition(
            identifier="doe",
            label="DOE",
            icon="folder-archive",
        )

        definition = TreeDefinition(
            identifier="project-documents",
            workspaces=(
                documentation_workspace,
                doe_workspace,
            ),
        )

        root = TreeNode(
            identifier="folder-plans",
            parent_identifier=None,
            label="Plans",
            kind=TreeNodeKind.BRANCH,
            source_object=object(),
        )

        child = TreeNode(
            identifier="document-plan-rdc",
            parent_identifier="folder-plans",
            label="Plan RDC",
            kind=TreeNodeKind.LEAF,
            source_object=object(),
            url="/documents/plan-rdc/",
        )

        self.runtime = EPTree(
            definition=definition,
            workspace_identifier="documentation",
            nodes=(
                root,
                child,
            ),
            commands=(
                TreeCommand(
                    definition=self.import_command_definition,
                    url="/documents/import/",
                    method="POST",
                ),
                TreeCommand(
                    definition=self.download_command_definition,
                    url="/documents/plans/download/",
                    is_visible=False,
                ),
            ),
            selected_node_identifier="document-plan-rdc",
        )

    def test_builder_exposes_active_workspace_and_tree(
        self,
    ) -> None:
        view_model = TreeViewModelBuilder().build(
            runtime=self.runtime,
        )

        self.assertEqual(
            view_model.identifier,
            "project-documents",
        )
        self.assertEqual(
            view_model.active_workspace.identifier,
            "documentation",
        )
        self.assertEqual(
            tuple(
                workspace.identifier
                for workspace in view_model.workspaces
            ),
            (
                "documentation",
                "doe",
            ),
        )
        self.assertTrue(
            view_model.workspaces[0].is_active
        )
        self.assertFalse(
            view_model.workspaces[1].is_active
        )

        root = view_model.root_nodes[0]
        child = root.children[0]

        self.assertEqual(root.icon, "folder")
        self.assertTrue(root.is_expanded)
        self.assertTrue(child.is_selected)
        self.assertEqual(
            child.url,
            "/documents/plan-rdc/",
        )

    def test_builder_keeps_only_visible_commands(
        self,
    ) -> None:
        view_model = TreeViewModelBuilder().build(
            runtime=self.runtime,
        )

        self.assertEqual(
            tuple(
                command.identifier
                for command in view_model.commands
            ),
            ("import",),
        )
        self.assertEqual(
            view_model.commands[0].method,
            "POST",
        )

    def test_builder_rejects_leaf_as_expanded_node(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "BRANCH",
        ):
            TreeViewModelBuilder().build(
                runtime=self.runtime,
                expanded_node_identifiers=(
                    "document-plan-rdc",
                ),
            )


if __name__ == "__main__":
    unittest.main()