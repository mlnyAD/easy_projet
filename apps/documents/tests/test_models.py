

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.models import (
    Document,
    DocumentFolder,
    DocumentHistory,
    DocumentVersion,
)
from apps.projects.models import Project
from apps.users.models import User
from apps.licenses.models import ClientEnvironment


class DocumentModelTestCase(TestCase):
    """
    Socle commun des tests du noyau documentaire.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test GED",
        )
        
        cls.client_environment = ClientEnvironment.objects.create(
            company=cls.company,
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_USER_GLOBAL_ROLE",
            label="Rôle global test",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_USER_ACCESS_LEVEL",
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

        # --------------------------------------------------------------
        # Utilisateur
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company,
            email="ged@example.com",
            first_name="Jean",
            last_name="Test",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_PROJECT_STATUS",
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
            reference="PRJ-GED-001",            
            name="Projet GED",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Catalogues documentaires
        # --------------------------------------------------------------

        cls.document_type_catalog = CatalogType.objects.create(
            code="TEST_DOCUMENT_TYPE",
            label="Type document test",
        )

        cls.document_status_catalog = CatalogType.objects.create(
            code="TEST_DOCUMENT_STATUS",
            label="Statut document test",
        )

        cls.document_lifecycle_catalog = CatalogType.objects.create(
            code="TEST_DOCUMENT_LIFECYCLE",
            label="Cycle documentaire test",
        )

        cls.document_type = CatalogValue.objects.create(
            catalog_type=cls.document_type_catalog,
            code="NOTE",
            label="Note technique",
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

        # --------------------------------------------------------------
        # Dossier racine
        # --------------------------------------------------------------

        cls.root_folder = DocumentFolder.objects.create(
            project=cls.project,
            name="Documents",
        )

    def create_document(
        self,
        *,
        title="Note technique",
        folder=None,
    ):
        return Document.objects.create(
            project=self.project,
            folder=folder or self.root_folder,
            title=title,
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user,
        )

    def create_version(
        self,
        document,
        version_number,
    ):
        return DocumentVersion.objects.create(
            document=document,
            version_number=version_number,
            original_filename=(
                f"note_v{version_number}.docx"
            ),
            storage_key=(
                f"documents/{document.pk}/"
                f"v{version_number}.docx"
            ),
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            file_size=1024,
            checksum=f"{version_number:064x}",
            created_by=self.user,
        )


class DocumentFolderTests(DocumentModelTestCase):

    def test_create_root_folder(self):
        folder = DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        self.assertEqual(
            folder.project,
            self.project,
        )

        self.assertIsNone(
            folder.parent,
        )

    def test_create_child_folder(self):
        folder = DocumentFolder.objects.create(
            project=self.project,
            parent=self.root_folder,
            name="Architecture",
        )

        self.assertEqual(
            folder.parent,
            self.root_folder,
        )

    def test_folder_cannot_be_its_own_parent(self):
        folder = DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        folder.parent = folder

        with self.assertRaises(ValidationError):
            folder.full_clean()

    def test_folder_parent_must_belong_to_same_project(self):
        other_project = Project.objects.create(
            company=self.company,
            reference="PRJ-GED-002",
            name="Autre projet",
            status=self.project_status,
        )

        other_folder = DocumentFolder.objects.create(
            project=other_project,
            name="Documents",
        )

        folder = DocumentFolder(
            project=self.project,
            parent=other_folder,
            name="Plans",
        )

        with self.assertRaises(ValidationError):
            folder.full_clean()

    def test_folder_cycle_is_rejected(self):
        child = DocumentFolder.objects.create(
            project=self.project,
            parent=self.root_folder,
            name="Plans",
        )

        grandchild = DocumentFolder.objects.create(
            project=self.project,
            parent=child,
            name="Exécution",
        )

        self.root_folder.parent = grandchild

        with self.assertRaises(ValidationError):
            self.root_folder.full_clean()

    def test_duplicate_root_folder_name_is_rejected(self):
        DocumentFolder.objects.create(
            project=self.project,
            name="Plans",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DocumentFolder.objects.create(
                    project=self.project,
                    name="Plans",
                )

    def test_duplicate_child_folder_name_is_rejected(self):
        DocumentFolder.objects.create(
            project=self.project,
            parent=self.root_folder,
            name="Plans",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DocumentFolder.objects.create(
                    project=self.project,
                    parent=self.root_folder,
                    name="Plans",
                )


class DocumentTests(DocumentModelTestCase):

    def test_create_document(self):
        document = self.create_document()

        self.assertEqual(
            document.project,
            self.project,
        )

        self.assertEqual(
            document.folder,
            self.root_folder,
        )

        self.assertIsNone(
            document.current_version,
        )

    def test_document_title_is_trimmed(self):
        document = self.create_document(
            title="   Note technique   ",
        )

        self.assertEqual(
            document.title,
            "Note technique",
        )

    def test_document_folder_must_belong_to_same_project(self):
        other_project = Project.objects.create(
            company=self.company,
            reference="PRJ-GED-003",
            name="Autre projet",
            status=self.project_status,
        )
        
        other_folder = DocumentFolder.objects.create(
            project=other_project,
            name="Documents",
        )

        document = Document(
            project=self.project,
            folder=other_folder,
            title="Document invalide",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user,
        )

        with self.assertRaises(ValidationError):
            document.full_clean()


class DocumentVersionTests(DocumentModelTestCase):

    def test_create_version(self):
        document = self.create_document()

        version = self.create_version(
            document,
            1,
        )

        self.assertEqual(
            version.version_number,
            1,
        )

        self.assertEqual(
            version.document,
            document,
        )

    def test_version_number_is_unique_per_document(self):
        document = self.create_document()

        self.create_version(
            document,
            1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_version(
                    document,
                    1,
                )

    def test_same_version_number_allowed_for_different_documents(self):
        document_1 = self.create_document(
            title="Document 1",
        )

        document_2 = self.create_document(
            title="Document 2",
        )

        version_1 = self.create_version(
            document_1,
            1,
        )

        version_2 = self.create_version(
            document_2,
            1,
        )

        self.assertEqual(
            version_1.version_number,
            version_2.version_number,
        )

    def test_current_version_must_belong_to_document(self):
        document_1 = self.create_document(
            title="Document 1",
        )

        document_2 = self.create_document(
            title="Document 2",
        )

        version = self.create_version(
            document_2,
            1,
        )

        document_1.current_version = version

        with self.assertRaises(ValidationError):
            document_1.full_clean()

    def test_current_version_can_reference_document_version(self):
        document = self.create_document()

        version = self.create_version(
            document,
            1,
        )

        document.current_version = version
        document.full_clean()
        document.save()

        document.refresh_from_db()

        self.assertEqual(
            document.current_version,
            version,
        )


class DocumentHistoryTests(DocumentModelTestCase):

    def test_create_history_entry_without_version(self):
        document = self.create_document()

        history = DocumentHistory.objects.create(
            document=document,
            action=DocumentHistory.Action.CREATED,
            user=self.user,
            details="Création du document.",
        )

        self.assertEqual(
            history.document,
            document,
        )

        self.assertIsNone(
            history.version,
        )

    def test_create_history_entry_with_version(self):
        document = self.create_document()

        version = self.create_version(
            document,
            1,
        )

        history = DocumentHistory.objects.create(
            document=document,
            version=version,
            action=(
                DocumentHistory.Action.VERSION_CREATED
            ),
            user=self.user,
            details="Création de la version 1.",
        )

        self.assertEqual(
            history.version,
            version,
        )