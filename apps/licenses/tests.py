

from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment, ClientEnvironmentMembership
from apps.licenses.models import License
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class LicenseAccessViewTests(TestCase):
    """
    Tests HTTP de la politique d'accès aux licences.

    Règles :
    - SYSTEM_ADMIN :
      consultation de toutes les licences,
      création et modification autorisées.
    - CLIENT_ADMIN :
      consultation des licences de son environnement,
      création et modification interdites.
    - PROJECT_MANAGER :
      consultation des licences des environnements
      correspondant à ses projets accessibles,
      création et modification interdites.
    - USER :
      aucune licence visible,
      création et modification interdites.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Licences HTTP",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Licences HTTP",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Niveau d'accès
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau accès test licences HTTP",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Rôle projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle sur projet",
        )

        cls.project_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut projet test licences HTTP",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut licence
        # --------------------------------------------------------------

        cls.license_status_type = CatalogType.objects.create(
            code="LICENSE_STATUS",
            label="Statut licence",
        )

        cls.license_status = CatalogValue.objects.create(
            catalog_type=cls.license_status_type,
            code="WAITING",
            label="En attente",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="license-http-system@example.com",
            first_name="System",
            last_name="Admin",
            is_system_admin=True,
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="license-http-client@example.com",
            first_name="Client",
            last_name="Admin",
        )

        # Employé par A mais affecté à un projet B.
        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="license-http-pm@example.com",
            first_name="Chef",
            last_name="Projet",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="license-http-user@example.com",
            first_name="Utilisateur",
            last_name="Standard",
        )

        # --------------------------------------------------------------
        # Appartenances aux environnements clients
        # --------------------------------------------------------------

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_b,
            user=cls.project_manager,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.standard_user,
        )

        # --------------------------------------------------------------
        # Licences
        # --------------------------------------------------------------

        cls.license_a = License.objects.create(
            client_environment=cls.environment_a,
            reference="LIC-HTTP-A",
            status=cls.license_status,
            project_capacity=1,
            granted_at=date(2026, 9, 1),
        )

        cls.license_b = License.objects.create(
            client_environment=cls.environment_b,
            reference="LIC-HTTP-B",
            status=cls.license_status,
            project_capacity=1,
            granted_at=date(2026, 9, 1),
        )

        # --------------------------------------------------------------
        # Projet B accessible au chef de projet
        # --------------------------------------------------------------

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-LIC-HTTP-B",
            name="Projet licences HTTP B",
            status=cls.project_status,
        )

        ProjectMembership.objects.create(
            project=cls.project_b,
            user=cls.project_manager,
            role=cls.project_role,
            access_level=cls.access_level,
            is_project_manager_responsible=True,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def login(self, user):
        self.client.force_login(user)

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_list_contains_all_licenses(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse("licenses:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.license_a.reference,
        )

        self.assertContains(
            response,
            self.license_b.reference,
        )

    def test_system_admin_create_returns_200(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse("licenses:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_system_admin_update_returns_200(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse(
                "licenses:update",
                kwargs={
                    "pk": self.license_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_list_only_contains_own_environment(self):
        self.login(self.client_admin)

        response = self.client.get(
            reverse("licenses:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.license_a.reference,
        )

        self.assertNotContains(
            response,
            self.license_b.reference,
        )

    def test_client_admin_create_returns_403(self):
        self.login(self.client_admin)

        response = self.client.get(
            reverse("licenses:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_client_admin_update_returns_403(self):
        self.login(self.client_admin)

        response = self.client.get(
            reverse(
                "licenses:update",
                kwargs={
                    "pk": self.license_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_list_uses_project_environment(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse("licenses:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            self.license_a.reference,
        )

        self.assertContains(
            response,
            self.license_b.reference,
        )

    def test_project_manager_create_returns_403(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse("licenses:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_project_manager_update_returns_403(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse(
                "licenses:update",
                kwargs={
                    "pk": self.license_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # ------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_list_contains_no_license(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse("licenses:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            self.license_a.reference,
        )

        self.assertNotContains(
            response,
            self.license_b.reference,
        )

    def test_standard_user_create_returns_403(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse("licenses:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_standard_user_update_returns_403(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse(
                "licenses:update",
                kwargs={
                    "pk": self.license_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )