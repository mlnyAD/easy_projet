

"""
Tests du service de gestion des sociétés participantes aux projets.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import Project, ProjectCompany
from apps.projects.services.project_company import ProjectCompanyService


class ProjectCompanyServiceTests(TestCase):
    """
    Tests cibles de ProjectCompanyService.
    """

    @classmethod
    def setUpTestData(cls):
        project_status_catalog = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut du projet",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=project_status_catalog,
            code="ACTIVE",
            label="Actif",
        )

        cls.responsible_company = Company.objects.create(
            name="Société responsable",
        )

        cls.client_environment = ClientEnvironment.objects.create(
            company=cls.responsible_company,
        )

        cls.participant_company = Company.objects.create(
            name="Société participante",
        )

        cls.project = Project.objects.create(
            reference="PRJ-001",
            name="Projet de test",
            company=cls.responsible_company,
            client_environment=cls.client_environment,
            status=cls.project_status,
        )

    def test_ensure_responsible_company_creates_participation(self):
        participation = (
            ProjectCompanyService.ensure_responsible_company(
                self.project
            )
        )

        self.assertEqual(
            participation.project,
            self.project,
        )
        self.assertEqual(
            participation.company,
            self.responsible_company,
        )
        self.assertTrue(
            ProjectCompany.objects.filter(
                project=self.project,
                company=self.responsible_company,
            ).exists()
        )

    def test_add_company_creates_participation(self):
        participation = ProjectCompanyService.add_company(
            self.project,
            self.participant_company,
        )

        self.assertEqual(
            participation.project,
            self.project,
        )
        self.assertEqual(
            participation.company,
            self.participant_company,
        )

    def test_add_company_is_idempotent(self):
        first = ProjectCompanyService.add_company(
            self.project,
            self.participant_company,
        )

        second = ProjectCompanyService.add_company(
            self.project,
            self.participant_company,
        )

        self.assertEqual(
            first.pk,
            second.pk,
        )
        self.assertEqual(
            ProjectCompany.objects.filter(
                project=self.project,
                company=self.participant_company,
            ).count(),
            1,
        )

    def test_remove_company_removes_participation(self):
        ProjectCompanyService.add_company(
            self.project,
            self.participant_company,
        )

        ProjectCompanyService.remove_company(
            self.project,
            self.participant_company,
        )

        self.assertFalse(
            ProjectCompany.objects.filter(
                project=self.project,
                company=self.participant_company,
            ).exists()
        )

    def test_remove_responsible_company_is_forbidden(self):
        ProjectCompanyService.ensure_responsible_company(
            self.project
        )

        with self.assertRaises(ValidationError):
            ProjectCompanyService.remove_company(
                self.project,
                self.responsible_company,
            )

        self.assertTrue(
            ProjectCompany.objects.filter(
                project=self.project,
                company=self.responsible_company,
            ).exists()
        )