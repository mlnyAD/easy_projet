

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.models import DocumentFolder
from apps.documents.services import DocumentFolderService
from apps.licenses.models import ClientEnvironment
from apps.projects.models import Project


class DocumentFolderServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test dossiers GED",
        )

        cls.client_environment = ClientEnvironment.objects.create(
            company=cls.company,
        )

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_FOLDER_PROJECT_STATUS",
            label="Statut projet test",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-GED-FOLDER-001",
            name="Projet dossiers GED",
            status=cls.project_status,
        )

    def test_create_root_folder(self):
        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        self.assertIsNotNone(folder.pk)
        self.assertEqual(folder.name, "Plans")
        self.assertIsNone(folder.parent)

    def test_create_child_folder(self):
        parent = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        child = DocumentFolderService.create_folder(
            project=self.project,
            parent=parent,
            name="RDC",
        )

        self.assertEqual(child.parent, parent)
        self.assertEqual(child.project, self.project)

    def test_create_folder_trims_name(self):
        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="   Administratif   ",
        )

        self.assertEqual(
            folder.name,
            "Administratif",
        )

    def test_create_folder_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            DocumentFolderService.create_folder(
                project=self.project,
                name="   ",
            )

    def test_create_duplicate_folder_is_rejected(self):
        DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        with self.assertRaises(ValueError):
            DocumentFolderService.create_folder(
                project=self.project,
                name="Plans",
            )

    def test_parent_must_belong_to_same_project(self):
        other_project = Project.objects.create(
            company=self.company,
            reference="PRJ-GED-FOLDER-002",
            name="Autre projet",
            status=self.project_status,
        )

        other_parent = DocumentFolder.objects.create(
            project=other_project,
            name="Autre dossier",
        )

        with self.assertRaises(ValueError):
            DocumentFolderService.create_folder(
                project=self.project,
                parent=other_parent,
                name="Sous-dossier",
            )

    def test_rename_folder(self):
        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        DocumentFolderService.rename_folder(
            folder=folder,
            name="Plans techniques",
        )

        folder.refresh_from_db()

        self.assertEqual(
            folder.name,
            "Plans techniques",
        )

    def test_rename_folder_trims_name(self):
        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        DocumentFolderService.rename_folder(
            folder=folder,
            name="   Plans techniques   ",
        )

        folder.refresh_from_db()

        self.assertEqual(
            folder.name,
            "Plans techniques",
        )

    def test_rename_duplicate_folder_is_rejected(self):
        DocumentFolderService.create_folder(
            project=self.project,
            name="Administratif",
        )

        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        with self.assertRaises(ValueError):
            DocumentFolderService.rename_folder(
                folder=folder,
                name="Administratif",
            )

    def test_delete_empty_folder(self):
        folder = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        folder_id = folder.pk

        DocumentFolderService.delete_folder(
            folder=folder,
        )

        self.assertFalse(
            DocumentFolder.objects.filter(
                pk=folder_id
            ).exists()
        )

    def test_delete_folder_with_child_is_rejected(self):
        parent = DocumentFolderService.create_folder(
            project=self.project,
            name="Plans",
        )

        DocumentFolderService.create_folder(
            project=self.project,
            parent=parent,
            name="RDC",
        )

        with self.assertRaises(ValueError):
            DocumentFolderService.delete_folder(
                folder=parent,
            )

    def test_invalid_dot_name_is_rejected(self):
        with self.assertRaises(ValueError):
            DocumentFolderService.create_folder(
                project=self.project,
                name="..",
            )