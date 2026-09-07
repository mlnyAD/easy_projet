

from datetime import date

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment, ClientEnvironmentMembership
from apps.licenses.models import License
from apps.licenses.services.access import (
    LicenseAccessService,
)
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.users.models import User


class LicenseAccessServiceTests(TestCase):
    """
    Tests de la politique d'accès aux licences.

    Deux environnements clients A et B sont créés.

    Les règles testées sont :
    - SYSTEM_ADMIN voit et administre tout ;
    - CLIENT_ADMIN voit uniquement son environnement ;
    - PROJECT_MANAGER voit les licences des environnements
      de ses projets accessibles ;
    - USER ne voit aucune licence.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Licences",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Licences",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Niveau d'accès utilisateur
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau accès test licences",
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
            label="Statut projet test licences",
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
            email="license-system-admin@example.com",
            first_name="System",
            last_name="Admin",
            is_system_admin=True,
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="license-client-admin@example.com",
            first_name="Client",
            last_name="Admin",
        )

        # Le chef de projet est volontairement employé par A,
        # mais sera membre uniquement d'un projet de B.
        #
        # Cela vérifie que son accès aux licences ne dépend pas
        # de user.company.client_environment.
        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="license-project-manager@example.com",
            first_name="Chef",
            last_name="Projet",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="license-user@example.com",
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
            reference="LIC-A",
            status=cls.license_status,
            project_capacity=1,
            granted_at=date(2026, 9, 1),
        )

        cls.license_b = License.objects.create(
            client_environment=cls.environment_b,
            reference="LIC-B",
            status=cls.license_status,
            project_capacity=1,
            granted_at=date(2026, 9, 1),
        )

        # --------------------------------------------------------------
        # Projet B
        # --------------------------------------------------------------

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-LIC-B",
            name="Projet licences B",
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
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_can_see_all_licenses(self):
        license_ids = set(
            LicenseAccessService
            .get_accessible_licenses(
                self.system_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            license_ids,
            {
                self.license_a.pk,
                self.license_b.pk,
            },
        )

    def test_system_admin_can_create_license(self):
        self.assertTrue(
            LicenseAccessService.can_create_license(
                self.system_admin
            )
        )

    def test_system_admin_can_update_license(self):
        self.assertTrue(
            LicenseAccessService.can_update_license(
                self.system_admin,
                self.license_a,
            )
        )

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_only_sees_own_environment(self):
        license_ids = set(
            LicenseAccessService
            .get_accessible_licenses(
                self.client_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            license_ids,
            {
                self.license_a.pk,
            },
        )

    def test_client_admin_cannot_create_license(self):
        self.assertFalse(
            LicenseAccessService.can_create_license(
                self.client_admin
            )
        )

    def test_client_admin_cannot_update_license(self):
        self.assertFalse(
            LicenseAccessService.can_update_license(
                self.client_admin,
                self.license_a,
            )
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_sees_project_environment_licenses(self):
        license_ids = set(
            LicenseAccessService
            .get_accessible_licenses(
                self.project_manager
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            license_ids,
            {
                self.license_b.pk,
            },
        )

    def test_project_manager_does_not_use_employer_environment(self):
        self.assertFalse(
            LicenseAccessService.can_view_license(
                self.project_manager,
                self.license_a,
            )
        )

        self.assertTrue(
            LicenseAccessService.can_view_license(
                self.project_manager,
                self.license_b,
            )
        )

    def test_project_manager_cannot_create_license(self):
        self.assertFalse(
            LicenseAccessService.can_create_license(
                self.project_manager
            )
        )

    def test_project_manager_cannot_update_license(self):
        self.assertFalse(
            LicenseAccessService.can_update_license(
                self.project_manager,
                self.license_b,
            )
        )

    # ------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_sees_no_license(self):
        self.assertFalse(
            LicenseAccessService
            .get_accessible_licenses(
                self.standard_user
            )
            .exists()
        )

    def test_standard_user_cannot_create_or_update_license(self):
        self.assertFalse(
            LicenseAccessService.can_create_license(
                self.standard_user
            )
        )

        self.assertFalse(
            LicenseAccessService.can_update_license(
                self.standard_user,
                self.license_a,
            )
        )

    # ------------------------------------------------------------------
    # Utilisateur inactif
    # ------------------------------------------------------------------

    def test_inactive_system_admin_has_no_access(self):
        self.system_admin.is_active = False
        self.system_admin.save(
            update_fields=["is_active"]
        )

        self.assertFalse(
            LicenseAccessService
            .get_accessible_licenses(
                self.system_admin
            )
            .exists()
        )

        self.assertFalse(
            LicenseAccessService.can_create_license(
                self.system_admin
            )
        )

        self.assertFalse(
            LicenseAccessService.can_update_license(
                self.system_admin,
                self.license_a,
            )
        )