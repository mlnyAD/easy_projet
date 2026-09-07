

"""
Tests d'intégration de ProjectCompany dans les vues Projet.
"""

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import Project, ProjectCompany
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class ProjectCompanyViewTests(TestCase):
    """
    Vérifie la synchronisation de la société responsable
    avec les sociétés participantes au projet.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société responsable",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.other_company = Company.objects.create(
            name="Nouvelle société responsable",
        )

        cls.other_client_environment = (
            ClientEnvironment.objects.create(
                company=cls.other_company,
            )
        )

        cls.project_status_type = (
            CatalogType.objects.create(
                code="PROJECT_STATUS",
                label="Statut projet",
            )
        )

        cls.project_status = (
            CatalogValue.objects.create(
                catalog_type=cls.project_status_type,
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
                is_default=True,
            )
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="project-company-admin@example.com",
            first_name="Jean",
            last_name="Administrateur",
            is_system_admin=True,
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    def build_project_data(
        self,
        *,
        reference,
        name,
        company,
    ):
        return {
            "reference": reference,
            "name": name,
            "description": "",
            "company": str(company.pk),
            "status": str(self.project_status.pk),
            "is_active": "on",
            "owner_company": "",
            "designer_company": "",
            "project_type": "",
            "contract_reference": "",
            "comments": "",
            "address_1": "",
            "address_2": "",
            "address_3": "",
            "postal_code": "",
            "city": "",
            "country": "",
            "planned_workload_hours": "0",
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "initial_receipt_date": "",
            "receipt_date": "",
            "initial_delivery_date": "",
            "delivery_date": "",
            "amount_quote_ht": "0.00",
            "amount_quote_ttc": "0.00",
            "amount_order_ht": "0.00",
            "amount_order_ttc": "0.00",
            "currency": "EUR",
            "budget_comments": "",
            "memberships-TOTAL_FORMS": "0",
            "memberships-INITIAL_FORMS": "0",
            "memberships-MIN_NUM_FORMS": "0",
            "memberships-MAX_NUM_FORMS": "1000",
            "external_participants-TOTAL_FORMS": "0",
            "external_participants-INITIAL_FORMS": "0",
            "external_participants-MIN_NUM_FORMS": "0",
            "external_participants-MAX_NUM_FORMS": "1000",
        }

    def test_create_adds_responsible_company(
        self,
    ):
        data = self.build_project_data(
            reference="PRJ-COMPANY-001",
            name="Projet création",
            company=self.company,
        )

        response = self.client.post(
            reverse("projects:create"),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        project = Project.objects.get(
            reference="PRJ-COMPANY-001",
        )

        self.assertTrue(
            ProjectCompany.objects.filter(
                project=project,
                company=self.company,
            ).exists()
        )

    def test_update_cannot_change_responsible_company(
        self,
    ):
        project = Project.objects.create(
            reference="PRJ-COMPANY-002",
            name="Projet modification",
            company=self.company,
            status=self.project_status,
        )

        ProjectCompany.objects.create(
            project=project,
            company=self.company,
        )

        data = self.build_project_data(
            reference=project.reference,
            name=project.name,
            company=self.other_company,
        )

        response = self.client.post(
            reverse(
                "projects:update",
                kwargs={
                    "pk": project.pk,
                },
            ),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        project.refresh_from_db()

        self.assertEqual(
            project.company,
            self.company,
        )

        self.assertTrue(
            ProjectCompany.objects.filter(
                project=project,
                company=self.company,
            ).exists()
        )

        self.assertFalse(
            ProjectCompany.objects.filter(
                project=project,
                company=self.other_company,
            ).exists()
        )