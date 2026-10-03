

from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase

from apps.documents.trees import (
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

        self.assertEqual(
            len(nodes),
            1,
        )

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