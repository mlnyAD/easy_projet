

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.models import (
    Document,
    DocumentFavorite,
    DocumentFolder,
)
from apps.documents.services import (
    DocumentFavoriteService,
)
from apps.projects.models import Project
from apps.users.models import User
from apps.licenses.models import ClientEnvironment


class DocumentFavoriteServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test favoris GED",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_FAV_ROLE",
            label="Rôle global test",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_FAV_ACCESS",
            label="Niveau accès test",
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
            email="favorite@example.com",
            first_name="Jean",
            last_name="Favori",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_FAV_PROJECT",
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
            reference="PRJ-GED-FAV-001",
            name="Projet favoris GED",
            status=cls.project_status,
        )

        cls.document_type_catalog = CatalogType.objects.create(
            code="TEST_FAV_DOC_TYPE",
            label="Type document test",
        )

        cls.document_status_catalog = CatalogType.objects.create(
            code="TEST_FAV_DOC_STATUS",
            label="Statut document test",
        )

        cls.document_lifecycle_catalog = CatalogType.objects.create(
            code="TEST_FAV_DOC_LIFE",
            label="Cycle documentaire test",
        )

        cls.document_type = CatalogValue.objects.create(
            catalog_type=cls.document_type_catalog,
            code="NOTE",
            label="Note",
            sort_order=10,
        )

        cls.document_status = CatalogValue.objects.create(
            catalog_type=cls.document_status_catalog,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.document_lifecycle = CatalogValue.objects.create(
            catalog_type=cls.document_lifecycle_catalog,
            code="ACTIVE",
            label="Actif",
            sort_order=10,
        )

        cls.folder = DocumentFolder.objects.create(
            project=cls.project,
            name="Documents",
        )

        cls.document = Document.objects.create(
            project=cls.project,
            folder=cls.folder,
            title="Document favori",
            document_type=cls.document_type,
            status=cls.document_status,
            lifecycle=cls.document_lifecycle,
            created_by=cls.user,
        )

    def test_add_favorite(self):
        favorite = DocumentFavoriteService.add_favorite(
            user=self.user,
            document=self.document,
        )

        self.assertIsNotNone(favorite.pk)

        self.assertTrue(
            DocumentFavorite.objects.filter(
                user=self.user,
                document=self.document,
            ).exists()
        )

    def test_add_favorite_is_idempotent(self):
        DocumentFavoriteService.add_favorite(
            user=self.user,
            document=self.document,
        )

        DocumentFavoriteService.add_favorite(
            user=self.user,
            document=self.document,
        )

        self.assertEqual(
            DocumentFavorite.objects.filter(
                user=self.user,
                document=self.document,
            ).count(),
            1,
        )

    def test_remove_favorite(self):
        DocumentFavoriteService.add_favorite(
            user=self.user,
            document=self.document,
        )

        DocumentFavoriteService.remove_favorite(
            user=self.user,
            document=self.document,
        )

        self.assertFalse(
            DocumentFavorite.objects.filter(
                user=self.user,
                document=self.document,
            ).exists()
        )

    def test_remove_favorite_is_idempotent(self):
        DocumentFavoriteService.remove_favorite(
            user=self.user,
            document=self.document,
        )

        DocumentFavoriteService.remove_favorite(
            user=self.user,
            document=self.document,
        )

        self.assertFalse(
            DocumentFavorite.objects.filter(
                user=self.user,
                document=self.document,
            ).exists()
        )