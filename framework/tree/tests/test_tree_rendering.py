

from unittest import TestCase

from framework.runtime import EPTree, TreeNode
from framework.tree import (
    TreeDefinition,
    TreeNodeKind,
    TreeWorkspaceDefinition,
)
from framework.viewmodel import TreeViewModelBuilder


class TreeRenderingTests(TestCase):
    def setUp(self) -> None:
        self.definition = TreeDefinition(
            identifier="document-tree",
            workspaces=(
                TreeWorkspaceDefinition(
                    identifier="documentation",
                    label="Documentation",
                    icon="folder-tree",
                ),
                TreeWorkspaceDefinition(
                    identifier="doe",
                    label="DOE",
                    icon="archive",
                ),
            ),
        )

    def test_builder_exposes_workspace_urls(self) -> None:
        runtime = EPTree(
            definition=self.definition,
            workspace_identifier="documentation",
            nodes=(
                TreeNode(
                    identifier="folder-plans",
                    parent_identifier=None,
                    label="Plans",
                    kind=TreeNodeKind.BRANCH,
                    source_object=object(),
                ),
            ),
        )

        view_model = TreeViewModelBuilder().build(
            runtime=runtime,
            workspace_urls={
                "documentation": "/documents/1/",
                "doe": "/documents/1/?workspace=doe",
            },
        )

        self.assertEqual(
            view_model.workspaces[0].url,
            "/documents/1/",
        )
        self.assertEqual(
            view_model.workspaces[1].url,
            "/documents/1/?workspace=doe",
        )

    def test_builder_exposes_node_data_attributes(self) -> None:
        runtime = EPTree(
            definition=self.definition,
            workspace_identifier="documentation",
            nodes=(
                TreeNode(
                    identifier="folder-plans",
                    parent_identifier=None,
                    label="Plans",
                    kind=TreeNodeKind.BRANCH,
                    source_object=object(),
                    data_attributes={
                        "folder-context": "",
                        "folder-id": "folder-plans",
                        "folder-is-doe": "false",
                    },
                ),
            ),
        )

        view_model = TreeViewModelBuilder().build(
            runtime=runtime,
        )

        node = view_model.root_nodes[0]

        self.assertEqual(
            node.data_attributes["folder-context"],
            "",
        )
        self.assertEqual(
            node.data_attributes["folder-id"],
            "folder-plans",
        )
        self.assertEqual(
            node.data_attributes["folder-is-doe"],
            "false",
        )

    def test_data_attribute_name_cannot_include_prefix(self) -> None:
        with self.assertRaises(ValueError):
            TreeNode(
                identifier="folder-plans",
                parent_identifier=None,
                label="Plans",
                kind=TreeNodeKind.BRANCH,
                source_object=object(),
                data_attributes={
                    "data-folder-id": "folder-plans",
                },
            )