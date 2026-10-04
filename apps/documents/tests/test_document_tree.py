

from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase

from apps.documents.trees import (
    DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER,
    DocumentFolderTreeNodeFactory,
)


class DocumentFolderTreeNodeFactoryTests(
    SimpleTestCase,
):
    def setUp(self) -> None:
        self.project = SimpleNamespace(
            pk=uuid4(),
        )

        self.folder = SimpleNamespace(
            pk=uuid4(),
            parent_id=None,
            name="Plans",
            is_doe=False,
            is_doe_root=False,
            is_doe_generated=False,
        )

    def test_build_exposes_existing_folder_contract(self):
        nodes = DocumentFolderTreeNodeFactory.build(
            project=self.project,
            folders=(self.folder,),
            selected_folder_id=self.folder.pk,
            return_url="/documents/projects/test/",
        )

        self.assertEqual(len(nodes), 1)

        node = nodes[0]

        self.assertEqual(
            node.identifier,
            str(self.folder.pk),
        )
        self.assertEqual(
            node.icon,
            "folder-open",
        )
        self.assertEqual(
            node.data_attributes["folder-name"],
            "Plans",
        )
        self.assertEqual(
            node.data_attributes["folder-is-doe"],
            "false",
        )
        self.assertEqual(
            node.data_attributes[
                "folder-doe-protected"
            ],
            "false",
        )
        self.assertIn(
            "/doe-selection/",
            node.data_attributes["folder-doe-url"],
        )

    def test_build_keeps_workspace_in_doe_folder_urls(self):
        doe_root = SimpleNamespace(
            pk=uuid4(),
            parent_id=None,
            name="DOE",
            is_doe=False,
            is_doe_root=True,
            is_doe_generated=False,
        )

        nodes = DocumentFolderTreeNodeFactory.build(
            project=self.project,
            folders=(doe_root,),
            selected_folder_id=None,
            return_url="/documents/projects/test/?workspace=doe",
            workspace_identifier=(
                DOCUMENT_EXPLORER_DOE_WORKSPACE_IDENTIFIER
            ),
        )

        self.assertEqual(len(nodes), 1)

        node = nodes[0]

        self.assertIn(
            "workspace=doe",
            node.url,
        )
        self.assertEqual(
            node.data_attributes[
                "folder-doe-protected"
            ],
            "true",
        )