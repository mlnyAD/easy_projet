

import json

from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.documents.integrations.providers import (
    OnlyOfficeJwtService,
)
from apps.documents.models import (
    Document,
    DocumentFolder,
    DocumentHistory,
    DocumentVersion,
)
from apps.documents.services import (
    DocumentAccessTokenService,
    DocumentService,
)
from apps.documents.storage import FileSystemDocumentStorage
from apps.projects.models import Project
from apps.users.models import User
from apps.licenses.models import ClientEnvironment

@override_settings(
    DEV_AUTO_LOGIN=False,
    ONLYOFFICE_JWT_SECRET=(
        "easy-projet-onlyoffice-test-secret-32chars"
    ),
)

class DocumentServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test GED",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

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

        cls.user = User.objects.create(
            company=cls.company,
            email="ged-document@example.com",
            first_name="Jean",
            last_name="Document",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

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
            reference="PRJ-GED-DOCUMENT-001",
            name="Projet GED Document",
            status=cls.project_status,
        )

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

        cls.root_folder = DocumentFolder.objects.create(
            project=cls.project,
            name="Documents",
        )

    def setUp(self):
        self.temporary_directory = TemporaryDirectory()

        self.storage = FileSystemDocumentStorage(
            self.temporary_directory.name
        )

        self.service = DocumentService(
            storage=self.storage
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def get_version_content_url(
        self,
        version,
        *,
        token=None,
    ):
        url = reverse(
            "documents:version-content",
            kwargs={
                "version_id": version.pk,
            },
        )

        if token is not None:
            url = f"{url}?token={token}"

        return url

    def create_imported_document_for_content_test(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Document à servir",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu transmis a ONLYOFFICE"),
            original_filename="document.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )

        document.refresh_from_db()

        return document, document.current_version

    def test_import_document_creates_document(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.assertIsNotNone(
            document.pk
        )

        self.assertEqual(
            Document.objects.count(),
            1,
        )

    def test_import_document_creates_first_version(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = document.versions.get()

        self.assertEqual(
            version.version_number,
            1,
        )

    def test_import_sets_current_version(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        document.refresh_from_db()

        self.assertIsNotNone(
            document.current_version
        )

        self.assertEqual(
            document.current_version.version_number,
            1,
        )

    def test_import_creates_physical_file(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        document.refresh_from_db()

        version = document.current_version

        self.assertIsNotNone(
            version
        )

        self.assertTrue(
            self.storage.exists(
                version.storage_key
            )
        )
    
    def test_import_creates_history(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        actions = list(
            DocumentHistory.objects
            .filter(document=document)
            .values_list(
                "action",
                flat=True,
            )
        )

        self.assertIn(
            DocumentHistory.Action.IMPORTED,
            actions,
        )

        self.assertIn(
            DocumentHistory.Action.VERSION_CREATED,
            actions,
        )

    def test_import_trims_title(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="   Note technique   ",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        self.assertEqual(
            document.title,
            "Note technique",
        )

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.import_document(
                project=self.project,
                folder=self.root_folder,
                title="   ",
                document_type=self.document_type,
                status=self.document_status,
                lifecycle=self.document_lifecycle,
                content=BytesIO(b"Contenu"),
                original_filename="note.docx",
                mime_type="application/test",
                user=self.user,
            )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_folder_must_belong_to_project(self):
        other_project = Project.objects.create(
            company=self.company,
            reference="PRJ-GED-DOCUMENT-002",
            name="Autre projet",
            status=self.project_status,
        )

        other_folder = DocumentFolder.objects.create(
            project=other_project,
            name="Documents",
        )

        with self.assertRaises(ValueError):
            self.service.import_document(
                project=self.project,
                folder=other_folder,
                title="Note technique",
                document_type=self.document_type,
                status=self.document_status,
                lifecycle=self.document_lifecycle,
                content=BytesIO(b"Contenu"),
                original_filename="note.docx",
                mime_type="application/test",
                user=self.user,
            )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_version_failure_rolls_back_document(self):
        with patch.object(
            self.service.version_service,
            "create_version",
            side_effect=RuntimeError(
                "Erreur volontaire"
            ),
        ):
            with self.assertRaises(RuntimeError):
                self.service.import_document(
                    project=self.project,
                    folder=self.root_folder,
                    title="Note technique",
                    document_type=self.document_type,
                    status=self.document_status,
                    lifecycle=self.document_lifecycle,
                    content=BytesIO(b"Contenu"),
                    original_filename="note.docx",
                    mime_type="application/test",
                    user=self.user,
                )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

        self.assertEqual(
            DocumentVersion.objects.count(),
            0,
        )
        
    def test_create_word_document(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu",
            document_format="word",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertIsNotNone(
            document.current_version
        )

        self.assertEqual(
            document.current_version.version_number,
            1,
        )

        self.assertEqual(
            document.current_version.original_filename,
            "Compte rendu.docx",
        )


    def test_create_excel_document(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Suivi financier",
            document_format="excel",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.current_version.original_filename,
            "Suivi financier.xlsx",
        )


    def test_create_powerpoint_document(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Présentation chantier",
            document_format="powerpoint",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.current_version.original_filename,
            "Présentation chantier.pptx",
        )


    def test_create_document_keeps_existing_extension(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu.docx",
            document_format="word",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.current_version.original_filename,
            "Compte rendu.docx",
        )


    def test_create_document_uses_expected_mime_type(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu",
            document_format="word",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.current_version.mime_type,
            (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )


    def test_create_document_creates_history(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu",
            document_format="word",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        actions = list(
            DocumentHistory.objects
            .filter(document=document)
            .values_list(
                "action",
                flat=True,
            )
        )

        self.assertIn(
            DocumentHistory.Action.CREATED,
            actions,
        )

        self.assertIn(
            DocumentHistory.Action.VERSION_CREATED,
            actions,
        )


    def test_create_document_rejects_unknown_format(self):
        with self.assertRaises(ValueError):
            self.service.create_document(
                project=self.project,
                folder=self.root_folder,
                title="Document PDF",
                document_format="pdf",
                document_type=self.document_type,
                status=self.document_status,
                lifecycle=self.document_lifecycle,
                user=self.user,
            )


    def test_create_document_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            self.service.create_document(
                project=self.project,
                folder=self.root_folder,
                title="   ",
                document_format="word",
                document_type=self.document_type,
                status=self.document_status,
                lifecycle=self.document_lifecycle,
                user=self.user,
            )


    def test_create_document_creates_physical_file(self):
        document = self.service.create_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu",
            document_format="word",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            user=self.user,
        )

        document.refresh_from_db()

        self.assertTrue(
            self.storage.exists(
                document.current_version.storage_key
            )
        )

    # ------------------------------------------------------------------
    # Accès au contenu d'une version
    # ------------------------------------------------------------------

    def test_version_content_with_valid_token(self):
        _, version = self.create_imported_document_for_content_test()

        token = DocumentAccessTokenService.create_token(
            version=version,
        )

        with patch(
            "apps.documents.views.content.get_document_storage",
            return_value=self.storage,
        ):
            response = self.client.get(
                self.get_version_content_url(
                    version,
                    token=token,
                )
            )

            content = b"".join(
                response.streaming_content
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            content,
            b"Contenu transmis a ONLYOFFICE",
        )

        self.assertEqual(
            response["Content-Type"],
            version.mime_type,
        )

        self.assertEqual(
            response["Content-Length"],
            str(version.file_size),
        )

        self.assertIn(
            version.original_filename,
            response["Content-Disposition"],
        )

    def test_version_content_without_token_is_rejected(self):
        _, version = self.create_imported_document_for_content_test()

        with patch(
            "apps.documents.views.content.get_document_storage",
            return_value=self.storage,
        ):
            response = self.client.get(
                self.get_version_content_url(
                    version,
                )
            )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_version_content_with_invalid_token_is_rejected(self):
        _, version = self.create_imported_document_for_content_test()

        with patch(
            "apps.documents.views.content.get_document_storage",
            return_value=self.storage,
        ):
            response = self.client.get(
                self.get_version_content_url(
                    version,
                    token="invalid-token",
                )
            )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_version_content_token_is_bound_to_version(self):
        _, version_1 = self.create_imported_document_for_content_test()

        document_2 = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Autre document",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Autre contenu"),
            original_filename="autre.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )
        document_2.refresh_from_db()
        version_2 = document_2.current_version

        token = DocumentAccessTokenService.create_token(
            version=version_1,
        )

        with patch(
            "apps.documents.views.content.get_document_storage",
            return_value=self.storage,
        ):
            response = self.client.get(
                self.get_version_content_url(
                    version_2,
                    token=token,
                )
            )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_version_content_missing_physical_file_returns_404(self):
        _, version = self.create_imported_document_for_content_test()

        token = DocumentAccessTokenService.create_token(
            version=version,
        )

        self.storage.delete(
            version.storage_key
        )

        with patch(
            "apps.documents.views.content.get_document_storage",
            return_value=self.storage,
        ):
            response = self.client.get(
                self.get_version_content_url(
                    version,
                    token=token,
                )
            )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Callback ONLYOFFICE
    # ------------------------------------------------------------------

    @staticmethod
    def get_version_callback_url(version):
        return reverse(
            "documents:version-callback",
            kwargs={
                "version_id": version.pk,
            },
        )

    def get_onlyoffice_authorization(self):
        token = OnlyOfficeJwtService.encode(
            {
                "iss": "onlyoffice-test",
            }
        )

        return f"Bearer {token}"

    def test_version_callback_accepts_valid_payload(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = document.versions.get()

        response = self.client.post(
            self.get_version_callback_url(version),
            data=json.dumps({"status": 1}),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_onlyoffice_authorization(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"error": 0})

    def test_version_callback_rejects_invalid_json(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = document.versions.get()

        response = self.client.post(
            self.get_version_callback_url(version),
            data="{invalid-json",
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_onlyoffice_authorization(),
        )

        self.assertEqual(response.status_code, 400)

    def test_version_callback_rejects_missing_status(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = document.versions.get()

        response = self.client.post(
            self.get_version_callback_url(version),
            data=json.dumps({}),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_onlyoffice_authorization(),
        )

        self.assertEqual(response.status_code, 400)

    def test_version_callback_rejects_non_integer_status(self):
        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Note technique",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu"),
            original_filename="note.docx",
            mime_type="application/test",
            user=self.user,
        )

        version = document.versions.get()

        response = self.client.post(
            self.get_version_callback_url(version),
            data=json.dumps({"status": "1"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_onlyoffice_authorization(),
        )

        self.assertEqual(response.status_code, 400)

    def test_version_callback_unknown_version_returns_404(self):
        from uuid import uuid4

        response = self.client.post(
            reverse(
                "documents:version-callback",
                kwargs={"version_id": uuid4()},
            ),
            data=json.dumps({"status": 1}),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_onlyoffice_authorization(),
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_callback."
        "get_document_storage"
    )
    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_callback."
        "OnlyOfficeDownloadService.download"
    )
    def test_version_callback_status_2_creates_v2(
        self,
        mocked_download,
        mocked_get_storage,
    ):
        mocked_get_storage.return_value = self.storage

        document = self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Document modifiable",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Version 1"),
            original_filename="document.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )

        document.refresh_from_db()
        version_1 = document.current_version

        mocked_download.return_value = BytesIO(
            b"Version 2 modifiee dans ONLYOFFICE"
        )

        token = OnlyOfficeJwtService.encode(
            {"iss": "onlyoffice-test"}
        )

        response = self.client.post(
            self.get_version_callback_url(version_1),
            data=json.dumps(
                {
                    "status": 2,
                    "url": (
                        "https://onlyoffice.example/"
                        "document.docx"
                    ),
                    "users": [
                        str(self.user.pk),
                    ],
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"error": 0})

        document.refresh_from_db()
        self.assertEqual(document.versions.count(), 2)

        version_2 = document.current_version

        self.assertIsNotNone(version_2)
        self.assertEqual(version_2.version_number, 2)
        self.assertNotEqual(version_2.pk, version_1.pk)
        self.assertEqual(version_2.original_filename, "document.docx")
        self.assertEqual(version_2.mime_type, version_1.mime_type)
        self.assertEqual(
            version_2.file_size,
            len(b"Version 2 modifiee dans ONLYOFFICE"),
        )
        self.assertTrue(
            self.storage.exists(version_2.storage_key)
        )

        history_exists = (
            DocumentHistory.objects
            .filter(
                document=document,
                version=version_2,
                action=DocumentHistory.Action.VERSION_CREATED,
            )
            .exists()
        )

        self.assertTrue(history_exists)

        mocked_download.assert_called_once_with(
            "https://onlyoffice.example/document.docx"
        )
