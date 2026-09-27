

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.client_configuration.models import (
    DocumentFolderTemplate,
    DocumentFolderTemplateFolder,
)
from apps.client_configuration.services.document_folder_template_application import (
    DocumentFolderTemplateApplicationService,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.documents.models import DocumentFolder
from apps.projects.models import Project


class DocumentFolderTemplateApplicationServiceTests(
    TestCase,
):
    """
    Tests de copie d'un modèle documentaire dans un projet.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test configuration client",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.project_status_type = (
            CatalogType.objects.create(
                code="TEST_CLIENT_CONFIG_PROJECT",
                label="Statut projet test",
            )
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

    def create_project(self, *, reference):
        return Project.objects.create(
            company=self.company,
            reference=reference,
            name=f"Projet {reference}",
            status=self.project_status,
        )

    def create_template(
        self,
        *,
        name="Arborescence chantier",
        is_default=True,
    ):
        return DocumentFolderTemplate.objects.create(
            client_environment=self.client_environment,
            name=name,
            is_default=is_default,
        )

    def test_no_folder_is_created_without_default_template(
        self,
    ):
        project = self.create_project(
            reference="PRJ-CONFIG-001",
        )

        created_count = (
            DocumentFolderTemplateApplicationService
            .apply_default_template(
                project=project,
            )
        )

        self.assertEqual(
            created_count,
            0,
        )

        self.assertFalse(
            DocumentFolder.objects.filter(
                project=project,
            ).exists()
        )

    def test_default_template_is_copied_to_project(
        self,
    ):
        template = self.create_template()

        administrative = (
            DocumentFolderTemplateFolder.objects.create(
                template=template,
                name="Administratif",
                sort_order=10,
            )
        )

        plans = (
            DocumentFolderTemplateFolder.objects.create(
                template=template,
                name="Plans",
                sort_order=20,
            )
        )

        DocumentFolderTemplateFolder.objects.create(
            template=template,
            parent=plans,
            name="Architecte",
            sort_order=10,
        )

        DocumentFolderTemplateFolder.objects.create(
            template=template,
            parent=plans,
            name="Exécution",
            sort_order=20,
        )

        project = self.create_project(
            reference="PRJ-CONFIG-002",
        )

        created_count = (
            DocumentFolderTemplateApplicationService
            .apply_default_template(
                project=project,
            )
        )

        self.assertEqual(
            created_count,
            4,
        )

        folders = DocumentFolder.objects.filter(
            project=project,
        ).order_by(
            "parent_id",
            "sort_order",
            "name",
        )

        self.assertEqual(
            folders.count(),
            4,
        )

        project_administrative = folders.get(
            name="Administratif",
        )

        project_plans = folders.get(
            name="Plans",
        )

        architect_folder = folders.get(
            name="Architecte",
        )

        execution_folder = folders.get(
            name="Exécution",
        )

        self.assertIsNone(
            project_administrative.parent,
        )

        self.assertIsNone(
            project_plans.parent,
        )

        self.assertEqual(
            architect_folder.parent,
            project_plans,
        )

        self.assertEqual(
            execution_folder.parent,
            project_plans,
        )

        self.assertEqual(
            project_administrative.sort_order,
            administrative.sort_order,
        )

        self.assertEqual(
            project_plans.sort_order,
            plans.sort_order,
        )

    def test_inactive_template_folder_is_not_copied(
        self,
    ):
        template = self.create_template()

        active_folder = (
            DocumentFolderTemplateFolder.objects.create(
                template=template,
                name="À conserver",
            )
        )

        DocumentFolderTemplateFolder.objects.create(
            template=template,
            name="À ignorer",
            is_active=False,
        )

        DocumentFolderTemplateFolder.objects.create(
            template=template,
            parent=active_folder,
            name="Sous-dossier conservé",
        )

        project = self.create_project(
            reference="PRJ-CONFIG-003",
        )

        created_count = (
            DocumentFolderTemplateApplicationService
            .apply_default_template(
                project=project,
            )
        )

        self.assertEqual(
            created_count,
            2,
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                project=project,
                name="À conserver",
            ).exists()
        )

        self.assertTrue(
            DocumentFolder.objects.filter(
                project=project,
                name="Sous-dossier conservé",
            ).exists()
        )

        self.assertFalse(
            DocumentFolder.objects.filter(
                project=project,
                name="À ignorer",
            ).exists()
        )