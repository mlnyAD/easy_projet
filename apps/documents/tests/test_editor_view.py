

from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.documents.integrations import registry
from apps.documents.integrations.providers import OnlyOfficeAdapter
from apps.documents.models import (
    DocumentFolder,
)
from apps.documents.services import DocumentService
from apps.documents.storage import FileSystemDocumentStorage
from apps.integrations.models import ExternalIntegration
from apps.projects.models import Project
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
    ONLYOFFICE_URL="https://onlyoffice.example.com",
    ONLYOFFICE_JWT_SECRET=(
        "easy-projet-onlyoffice-test-secret-32chars"
    ),
    EASY_PROJET_PUBLIC_URL=(
        "https://easy-projet.example.com"
    ),
)
class DocumentEditorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société / environnement
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test éditeur",
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
            code="TEST_EDITOR_USER_GLOBAL_ROLE",
            label="Rôle global test",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_EDITOR_USER_ACCESS_LEVEL",
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
            email="editor@example.com",
            first_name="Jean",
            last_name="Editeur",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_EDITOR_PROJECT_STATUS",
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
            reference="PRJ-GED-EDITOR-001",
            name="Projet éditeur GED",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Catalogues documentaires
        # --------------------------------------------------------------

        cls.document_type_catalog = CatalogType.objects.create(
            code="TEST_EDITOR_DOCUMENT_TYPE",
            label="Type document test",
        )

        cls.document_status_catalog = CatalogType.objects.create(
            code="TEST_EDITOR_DOCUMENT_STATUS",
            label="Statut document test",
        )

        cls.document_lifecycle_catalog = CatalogType.objects.create(
            code="TEST_EDITOR_DOCUMENT_LIFECYCLE",
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

        # --------------------------------------------------------------
        # Catalogues des intégrations externes
        # --------------------------------------------------------------

        cls.integration_service_catalog = (
            CatalogType.objects.create(
                code="INTEGRATION_SERVICE_TYPE",
                label="Type de service",
            )
        )

        cls.integration_provider_catalog = (
            CatalogType.objects.create(
                code="INTEGRATION_PROVIDER",
                label="Fournisseur",
            )
        )

        cls.integration_status_catalog = (
            CatalogType.objects.create(
                code="INTEGRATION_CONNECTION_STATUS",
                label="État de connexion",
            )
        )

        cls.office_service = CatalogValue.objects.create(
            catalog_type=cls.integration_service_catalog,
            code="OFFICE",
            label="Suite bureautique",
            sort_order=10,
        )

        cls.onlyoffice_provider = CatalogValue.objects.create(
            catalog_type=cls.integration_provider_catalog,
            code="ONLYOFFICE",
            label="ONLYOFFICE",
            sort_order=10,
        )

        cls.connected_status = CatalogValue.objects.create(
            catalog_type=cls.integration_status_catalog,
            code="CONNECTED",
            label="Connectée",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Intégration ONLYOFFICE
        # --------------------------------------------------------------

        cls.external_integration = (
            ExternalIntegration.objects.create(
                client_environment=cls.client_environment,
                service_type=cls.office_service,
                provider=cls.onlyoffice_provider,
                connection_status=cls.connected_status,
                code="ONLYOFFICE_EDITOR",
                name="ONLYOFFICE",
                priority=10,
                is_active=True,
            )
        )

    def setUp(self):
        self.temporary_directory = TemporaryDirectory()

        self.storage = FileSystemDocumentStorage(
            self.temporary_directory.name
        )

        self.service = DocumentService(
            storage=self.storage
        )

        # Le registre global doit connaître l'adaptateur.
        try:
            registry.get("ONLYOFFICE")
        except LookupError:
            registry.register(
                OnlyOfficeAdapter()
            )

        self.client.force_login(
            self.user
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_document(self):
        return self.service.import_document(
            project=self.project,
            folder=self.root_folder,
            title="Compte rendu",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Version 1"),
            original_filename="compte_rendu.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )

    @staticmethod
    def get_editor_url(version):
        return reverse(
            "documents:version-edit",
            kwargs={
                "version_id": version.pk,
            },
        )

    # ------------------------------------------------------------------
    # Ouverture
    # ------------------------------------------------------------------

    def test_current_version_opens_editor(self):
        document = self.create_document()

        document.refresh_from_db()

        version = document.current_version

        response = self.client.get(
            self.get_editor_url(version)
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "documents/document_editor.html",
        )

    # ------------------------------------------------------------------
    # Configuration transmise au template
    # ------------------------------------------------------------------

    def test_editor_context_contains_onlyoffice_config(self):
        document = self.create_document()

        document.refresh_from_db()

        version = document.current_version

        response = self.client.get(
            self.get_editor_url(version)
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["document"],
            document,
        )

        self.assertEqual(
            response.context["version"],
            version,
        )

        self.assertEqual(
            response.context["onlyoffice_api_url"],
            (
                "https://onlyoffice.example.com/"
                "web-apps/apps/api/documents/api.js"
            ),
        )

        config = response.context[
            "onlyoffice_config"
        ]

        self.assertEqual(
            config["documentType"],
            "word",
        )

        self.assertEqual(
            config["document"]["fileType"],
            "docx",
        )

        self.assertEqual(
            config["document"]["key"],
            str(version.pk),
        )

        self.assertEqual(
            config["editorConfig"]["mode"],
            "edit",
        )

        self.assertEqual(
            config["editorConfig"]["user"]["id"],
            str(self.user.pk),
        )

        self.assertIn(
            "token",
            config,
        )

    # ------------------------------------------------------------------
    # Version ancienne
    # ------------------------------------------------------------------

    def test_old_version_cannot_be_edited(self):
        document = self.create_document()

        document.refresh_from_db()

        version_1 = document.current_version

        self.service.version_service.create_version(
            document=document,
            content=BytesIO(b"Version 2"),
            original_filename="compte_rendu.docx",
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            user=self.user,
        )

        document.refresh_from_db()

        self.assertNotEqual(
            document.current_version_id,
            version_1.pk,
        )

        response = self.client.get(
            self.get_editor_url(version_1)
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Intégration absente
    # ------------------------------------------------------------------

    def test_missing_office_integration_returns_404(self):
        document = self.create_document()

        document.refresh_from_db()

        version = document.current_version

        ExternalIntegration.objects.filter(
            pk=self.external_integration.pk
        ).delete()

        response = self.client.get(
            self.get_editor_url(version)
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Intégration inactive
    # ------------------------------------------------------------------

    def test_inactive_office_integration_returns_404(self):
        document = self.create_document()

        document.refresh_from_db()

        version = document.current_version

        ExternalIntegration.objects.filter(
            pk=self.external_integration.pk
        ).update(
            is_active=False
        )

        response = self.client.get(
            self.get_editor_url(version)
        )

        self.assertEqual(
            response.status_code,
            404,
        )