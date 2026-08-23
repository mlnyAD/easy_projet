

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.models import DocumentFolder
from apps.licenses.models import ClientEnvironment
from apps.projects.models import Project
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class DocumentFolderViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test vues dossiers GED",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.global_role_type = (
            CatalogType.objects.create(
                code="TEST_FOLDER_ROLE",
                label="Rôle global test",
            )
        )

        cls.access_level_type = (
            CatalogType.objects.create(
                code="TEST_FOLDER_LEVEL",
                label="Niveau accès test",
            )
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="folder-view@example.com",
            first_name="Jean",
            last_name="Dossier",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.project_status_type = (
            CatalogType.objects.create(
                code="TEST_FOLDER_PROJECT",
                label="Statut projet test",
            )
        )

        cls.project_status = (
            CatalogValue.objects.create(
                catalog_type=cls.project_status_type,
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
            )
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-GED-FOLDER-VIEW-001",
            name="Projet vues dossiers GED",
            status=cls.project_status,
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    def test_create_root_folder(self):
        response = self.client.post(
            reverse(
                "documents:folder-create",
                kwargs={
                    "project_id": self.project.pk,
                },
            ),
            {
                "name": "Plans",
            },
        )

        folder = DocumentFolder.objects.get(
            project=self.project,
            name="Plans",
        )

        self.assertRedirects(
            response,
            reverse(
                "documents:folder",
                kwargs={
                    "project_id": self.project.pk,
                    "folder_id": folder.pk,
                },
            ),
        )

    def test_create_child_folder(self):
        parent = DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        response = self.client.post(
            reverse(
                "documents:folder-create",
                kwargs={
                    "project_id": self.project.pk,
                },
            ),
            {
                "name": "RDC",
                "parent_id": str(parent.pk),
            },
        )

        folder = DocumentFolder.objects.get(
            project=self.project,
            parent=parent,
            name="RDC",
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            folder.parent,
            parent,
        )

    def test_create_duplicate_returns_400(self):
        DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        response = self.client.post(
            reverse(
                "documents:folder-create",
                kwargs={
                    "project_id": self.project.pk,
                },
            ),
            {
                "name": "Plans",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_rename_folder(self):
        folder = DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        response = self.client.post(
            reverse(
                "documents:folder-rename",
                kwargs={
                    "project_id": self.project.pk,
                    "folder_id": folder.pk,
                },
            ),
            {
                "name": "Plans techniques",
            },
        )

        folder.refresh_from_db()

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            folder.name,
            "Plans techniques",
        )

    def test_delete_empty_folder(self):
        folder = DocumentFolder.objects.create(
            project=self.project,
            name="À supprimer",
        )

        response = self.client.post(
            reverse(
                "documents:folder-delete",
                kwargs={
                    "project_id": self.project.pk,
                    "folder_id": folder.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            DocumentFolder.objects.filter(
                pk=folder.pk,
            ).exists()
        )

    def test_delete_non_empty_folder_returns_400(self):
        parent = DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        DocumentFolder.objects.create(
            project=self.project,
            parent=parent,
            name="RDC",
        )

        response = self.client.post(
            reverse(
                "documents:folder-delete",
                kwargs={
                    "project_id": self.project.pk,
                    "folder_id": parent.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                pk=parent.pk,
            ).exists()
        )