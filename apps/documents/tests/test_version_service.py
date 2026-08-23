

from hashlib import sha256
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.models import (
    Document,
    DocumentHistory,
    DocumentVersion,
)
from apps.documents.services import DocumentVersionService
from apps.documents.storage import FileSystemDocumentStorage
from apps.projects.models import Project
from apps.users.models import User

# Adapter uniquement cet import si ClientEnvironment
# se trouve dans un autre module.
from apps.licenses.models import ClientEnvironment


class DocumentVersionServiceTests(TestCase):
    """
    Tests du service de création des versions documentaires.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test GED",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
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
            email="ged-version@example.com",
            first_name="Jean",
            last_name="Version",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statut du projet
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

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-GED-VERSION-001",
            name="Projet GED Version",
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
        # Dossier documentaire
        # --------------------------------------------------------------

        from apps.documents.models import DocumentFolder

        cls.root_folder = DocumentFolder.objects.create(
            project=cls.project,
            name="Documents",
        )

    def setUp(self):
        self.temporary_directory = TemporaryDirectory()

        self.storage = FileSystemDocumentStorage(
            self.temporary_directory.name
        )

        self.service = DocumentVersionService(
            storage=self.storage
        )

        self.document = Document.objects.create(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_first_version(self):
        version = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 1"),
            original_filename="note.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )

        self.assertEqual(
            version.version_number,
            1,
        )

        self.assertTrue(
            self.storage.exists(
                version.storage_key
            )
        )

    def test_create_second_version(self):
        self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 1"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 2"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.assertEqual(
            version.version_number,
            2,
        )

        self.assertEqual(
            self.document.versions.count(),
            2,
        )

    # ------------------------------------------------------------------
    # Métadonnées techniques
    # ------------------------------------------------------------------

    def test_checksum_is_sha256(self):
        content = b"Contenu Easy Projet"

        version = self.service.create_version(
            document=self.document,
            content=BytesIO(content),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.assertEqual(
            version.checksum,
            sha256(content).hexdigest(),
        )

    def test_file_size_is_calculated(self):
        content = b"1234567890"

        version = self.service.create_version(
            document=self.document,
            content=BytesIO(content),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.assertEqual(
            version.file_size,
            len(content),
        )

    def test_client_path_is_removed_from_filename(self):
        version = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 1"),
            original_filename=(
                "C:/Users/test/Documents/note.docx"
            ),
            mime_type="application/test",
            user=self.user,
        )

        self.assertEqual(
            version.original_filename,
            "note.docx",
        )

    # ------------------------------------------------------------------
    # Version courante
    # ------------------------------------------------------------------

    def test_current_version_is_updated(self):
        version_1 = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 1"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.current_version,
            version_1,
        )

        version_2 = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 2"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.current_version,
            version_2,
        )

    # ------------------------------------------------------------------
    # Historique
    # ------------------------------------------------------------------

    def test_history_is_created(self):
        version = self.service.create_version(
            document=self.document,
            content=BytesIO(b"Version 1"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        history = DocumentHistory.objects.get(
            document=self.document,
            action=(
                DocumentHistory.Action.VERSION_CREATED
            ),
        )

        self.assertEqual(
            history.version,
            version,
        )

        self.assertEqual(
            history.user,
            self.user,
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_empty_content_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.create_version(
                document=self.document,
                content=BytesIO(b""),
                original_filename="note.docx",
                mime_type="application/test",
                user=self.user,
            )

        self.assertEqual(
            DocumentVersion.objects.filter(
                document=self.document
            ).count(),
            0,
        )

    # ------------------------------------------------------------------
    # Cohérence stockage / base
    # ------------------------------------------------------------------

    def test_database_failure_removes_physical_file(self):
        with patch.object(
            DocumentVersion.objects,
            "create",
            side_effect=IntegrityError(
                "Erreur volontaire de test"
            ),
        ):
            with self.assertRaises(IntegrityError):
                self.service.create_version(
                    document=self.document,
                    content=BytesIO(b"Version 1"),
                    original_filename="note.docx",
                    mime_type="application/test",
                    user=self.user,
                )

        self.assertEqual(
            DocumentVersion.objects.filter(
                document=self.document
            ).count(),
            0,
        )

        files = [
            path
            for path in self.storage.root.rglob("*")
            if path.is_file()
        ]

        self.assertEqual(
            files,
            [],
        )