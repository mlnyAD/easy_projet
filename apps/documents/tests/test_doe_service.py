

from __future__ import annotations

from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.client_configuration.models import (
    DoeTemplate,
    DoeTemplateFolder,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.documents.models import (
    Document,
    DocumentFolder,
    DoeGeneration,
)
from apps.documents.services.document_service import (
    DocumentService,
)
from apps.documents.services.doe_service import DoeService
from apps.documents.storage import FileSystemDocumentStorage
from apps.projects.models import Project
from apps.users.models import User


class DoeServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test DOE",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="doe@example.com",
            first_name="Jean",
            last_name="DOE",
        )

        cls.project_status_type = (
            CatalogType.objects.create(
                code="TEST_DOE_PROJECT_STATUS",
                label="Statut projet test DOE",
            )
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.document_type_catalog = (
            CatalogType.objects.create(
                code="TEST_DOE_DOCUMENT_TYPE",
                label="Type documentaire test DOE",
            )
        )

        cls.document_status_catalog = (
            CatalogType.objects.create(
                code="TEST_DOE_DOCUMENT_STATUS",
                label="Statut documentaire test DOE",
            )
        )

        cls.document_lifecycle_catalog = (
            CatalogType.objects.create(
                code="TEST_DOE_DOCUMENT_LIFECYCLE",
                label="Cycle documentaire test DOE",
            )
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

    def setUp(self):
        self.project = Project.objects.create(
            company=self.company,
            reference=(
                f"PRJ-DOE-{self._testMethodName[-8:].upper()}"
            ),
            name="Projet test DOE",
            status=self.project_status,
        )

        self.temporary_directory = TemporaryDirectory()

        self.document_service = DocumentService(
            storage=FileSystemDocumentStorage(
                self.temporary_directory.name
            )
        )

        self.service = DoeService(
            document_service=self.document_service
        )

        self.source_root = DocumentFolder.objects.create(
            project=self.project,
            name="Documents",
            sort_order=10,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_source_document(
        self,
        *,
        title="Document DOE",
        folder=None,
        is_doe=False,
    ) -> Document:
        document = self.document_service.import_document(
            project=self.project,
            folder=folder or self.source_root,
            title=title,
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(b"Contenu documentaire de test"),
            original_filename=f"{title}.pdf",
            mime_type="application/pdf",
            user=self.user,
        )

        if is_doe:
            document.is_doe = True
            document.save(
                update_fields=[
                    "is_doe",
                    "updated_at",
                ]
            )

        return document

    def create_doe_template(
        self,
        *,
        name="DOE type test",
    ) -> DoeTemplate:
        return DoeTemplate.objects.create(
            client_environment=self.client_environment,
            name=name,
        )

    def test_generate_without_template_mirrors_source_tree(self):
        source_child = DocumentFolder.objects.create(
            project=self.project,
            parent=self.source_root,
            name="Plans",
            sort_order=20,
        )

        source_document = self.create_source_document(
            title="Plan niveau 1",
            folder=source_child,
            is_doe=True,
        )

        generation = self.service.generate(
            project=self.project,
            user=self.user,
        )

        self.assertIsNotNone(generation)
        self.assertIsNone(generation.doe_template)
        self.assertEqual(generation.document_count, 1)

        doe_root = DocumentFolder.objects.get(
            project=self.project,
            is_doe_root=True,
        )

        destination_root = DocumentFolder.objects.get(
            project=self.project,
            parent=doe_root,
            name="Documents",
            is_doe_generated=True,
        )

        destination_child = DocumentFolder.objects.get(
            project=self.project,
            parent=destination_root,
            name="Plans",
            is_doe_generated=True,
        )

        generated_document = Document.objects.get(
            project=self.project,
            is_doe_generated=True,
        )

        self.assertEqual(
            generated_document.folder,
            destination_child,
        )
        self.assertEqual(
            generated_document.doe_source_document,
            source_document,
        )

    def test_generate_with_template_creates_structure_and_to_sort_folder(
        self,
    ):
        doe_template = self.create_doe_template()

        administrative = DoeTemplateFolder.objects.create(
            template=doe_template,
            name="Administratif",
            sort_order=10,
        )

        DoeTemplateFolder.objects.create(
            template=doe_template,
            parent=administrative,
            name="Procès-verbaux",
            sort_order=10,
        )

        source_document = self.create_source_document(
            title="Compte rendu chantier",
            is_doe=True,
        )

        generation = self.service.generate(
            project=self.project,
            user=self.user,
            doe_template=doe_template,
        )

        self.assertEqual(
            generation.doe_template,
            doe_template,
        )
        self.assertEqual(generation.document_count, 1)

        doe_root = DocumentFolder.objects.get(
            project=self.project,
            is_doe_root=True,
        )

        administrative_folder = DocumentFolder.objects.get(
            project=self.project,
            parent=doe_root,
            name="Administratif",
            is_doe_generated=True,
        )

        DocumentFolder.objects.get(
            project=self.project,
            parent=administrative_folder,
            name="Procès-verbaux",
            is_doe_generated=True,
        )

        to_sort_folder = DocumentFolder.objects.get(
            project=self.project,
            parent=doe_root,
            name=DoeService.TO_SORT_FOLDER_NAME,
            is_doe_generated=True,
        )

        generated_document = Document.objects.get(
            project=self.project,
            is_doe_generated=True,
        )

        self.assertEqual(
            generated_document.folder,
            to_sort_folder,
        )
        self.assertEqual(
            generated_document.doe_source_document,
            source_document,
        )

    def test_generate_with_template_creates_empty_structure(
        self,
    ):
        doe_template = self.create_doe_template()

        DoeTemplateFolder.objects.create(
            template=doe_template,
            name="Administratif",
            sort_order=10,
        )

        generation = self.service.generate(
            project=self.project,
            user=self.user,
            doe_template=doe_template,
        )

        self.assertIsNotNone(generation)
        self.assertEqual(generation.document_count, 0)

        doe_root = DocumentFolder.objects.get(
            project=self.project,
            is_doe_root=True,
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                project=self.project,
                parent=doe_root,
                name="Administratif",
                is_doe_generated=True,
            ).exists()
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                project=self.project,
                parent=doe_root,
                name=DoeService.TO_SORT_FOLDER_NAME,
                is_doe_generated=True,
            ).exists()
        )

    def test_generate_without_template_and_without_selection_returns_none(
        self,
    ):
        self.create_source_document(
            title="Document non sélectionné",
        )

        generation = self.service.generate(
            project=self.project,
            user=self.user,
        )

        self.assertIsNone(generation)

        self.assertFalse(
            DocumentFolder.objects.filter(
                project=self.project,
                is_doe_root=True,
            ).exists()
        )

        self.assertFalse(
            DoeGeneration.objects.filter(
                project=self.project,
            ).exists()
        )

    def test_regeneration_replaces_previous_generated_content(
        self,
    ):
        first_template = self.create_doe_template(
            name="DOE type initial",
        )

        DoeTemplateFolder.objects.create(
            template=first_template,
            name="Ancienne structure",
        )

        second_template = self.create_doe_template(
            name="DOE type final",
        )

        DoeTemplateFolder.objects.create(
            template=second_template,
            name="Nouvelle structure",
        )

        self.create_source_document(
            title="Document sélectionné",
            is_doe=True,
        )

        self.service.generate(
            project=self.project,
            user=self.user,
            doe_template=first_template,
        )

        self.service.generate(
            project=self.project,
            user=self.user,
            doe_template=second_template,
        )

        self.assertFalse(
            DocumentFolder.objects.filter(
                project=self.project,
                name="Ancienne structure",
                is_doe_generated=True,
            ).exists()
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                project=self.project,
                name="Nouvelle structure",
                is_doe_generated=True,
            ).exists()
        )

        self.assertEqual(
            Document.objects.filter(
                project=self.project,
                is_doe_generated=True,
            ).count(),
            1,
        )

        latest_generation = (
            DoeGeneration.objects
            .filter(project=self.project)
            .order_by("-created_at")
            .first()
        )

        self.assertEqual(
            latest_generation.doe_template,
            second_template,
        )