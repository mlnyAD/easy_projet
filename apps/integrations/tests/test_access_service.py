

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.integrations.models import ExternalIntegration
from apps.integrations.services.access import (
    IntegrationAccessService,
)
from apps.users.models import User


class IntegrationAccessServiceTests(TestCase):
    """
    Tests de la politique d'accès aux intégrations externes.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Intégrations",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Intégrations",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Rôles globaux
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="USER_GLOBAL_ROLE",
            label="Rôle global",
        )

        cls.system_admin_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="SYSTEM_ADMIN",
            label="Administrateur système",
            sort_order=10,
        )

        cls.client_admin_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="CLIENT_ADMIN",
            label="Administrateur client",
            sort_order=20,
        )

        cls.project_manager_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=30,
        )

        cls.user_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=40,
        )

        # --------------------------------------------------------------
        # Niveau d'accès
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_INT_ACCESS_LEVEL",
            label="Niveau accès test intégrations",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Catalogues intégrations
        # --------------------------------------------------------------

        cls.service_type_catalog = CatalogType.objects.create(
            code="INTEGRATION_SERVICE_TYPE",
            label="Type de service",
        )

        cls.service_type = CatalogValue.objects.create(
            catalog_type=cls.service_type_catalog,
            code="DOCUMENT",
            label="Document",
            sort_order=10,
        )

        cls.provider_catalog = CatalogType.objects.create(
            code="INTEGRATION_PROVIDER",
            label="Fournisseur",
        )

        cls.provider = CatalogValue.objects.create(
            catalog_type=cls.provider_catalog,
            code="TEST_PROVIDER",
            label="Fournisseur test",
            sort_order=10,
        )

        cls.status_catalog = CatalogType.objects.create(
            code="INTEGRATION_CONNECTION_STATUS",
            label="État de connexion",
        )

        cls.connection_status = CatalogValue.objects.create(
            catalog_type=cls.status_catalog,
            code="CONNECTED",
            label="Connecté",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="integration-system@example.com",
            first_name="System",
            last_name="Admin",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        cls.client_admin_a = User.objects.create(
            company=cls.company_a,
            email="integration-client-a@example.com",
            first_name="Client",
            last_name="Admin A",
            global_role=cls.client_admin_role,
            access_level=cls.access_level,
        )

        cls.client_admin_b = User.objects.create(
            company=cls.company_b,
            email="integration-client-b@example.com",
            first_name="Client",
            last_name="Admin B",
            global_role=cls.client_admin_role,
            access_level=cls.access_level,
        )

        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="integration-pm@example.com",
            first_name="Chef",
            last_name="Projet",
            global_role=cls.project_manager_role,
            access_level=cls.access_level,
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="integration-user@example.com",
            first_name="Utilisateur",
            last_name="Standard",
            global_role=cls.user_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Intégrations
        # --------------------------------------------------------------

        cls.integration_a = ExternalIntegration.objects.create(
            client_environment=cls.environment_a,
            service_type=cls.service_type,
            provider=cls.provider,
            connection_status=cls.connection_status,
            code="INT-A",
            name="Intégration A",
            priority=100,
        )

        cls.integration_b = ExternalIntegration.objects.create(
            client_environment=cls.environment_b,
            service_type=cls.service_type,
            provider=cls.provider,
            connection_status=cls.connection_status,
            code="INT-B",
            name="Intégration B",
            priority=100,
        )

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_sees_all_integrations(self):
        integration_ids = set(
            IntegrationAccessService
            .get_accessible_integrations(
                self.system_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            integration_ids,
            {
                self.integration_a.pk,
                self.integration_b.pk,
            },
        )

    def test_system_admin_can_assign_all_active_environments(self):
        environment_ids = set(
            IntegrationAccessService
            .get_assignable_environments(
                self.system_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            environment_ids,
            {
                self.environment_a.pk,
                self.environment_b.pk,
            },
        )

    def test_system_admin_can_create_and_update(self):
        self.assertTrue(
            IntegrationAccessService.can_create_integration(
                self.system_admin
            )
        )

        self.assertTrue(
            IntegrationAccessService.can_update_integration(
                self.system_admin,
                self.integration_b,
            )
        )

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_only_sees_own_environment(self):
        integration_ids = set(
            IntegrationAccessService
            .get_accessible_integrations(
                self.client_admin_a
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            integration_ids,
            {
                self.integration_a.pk,
            },
        )

    def test_client_admin_only_assigns_own_environment(self):
        environment_ids = set(
            IntegrationAccessService
            .get_assignable_environments(
                self.client_admin_a
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            environment_ids,
            {
                self.environment_a.pk,
            },
        )

    def test_client_admin_can_create(self):
        self.assertTrue(
            IntegrationAccessService.can_create_integration(
                self.client_admin_a
            )
        )

    def test_client_admin_can_update_own_integration(self):
        self.assertTrue(
            IntegrationAccessService.can_update_integration(
                self.client_admin_a,
                self.integration_a,
            )
        )

    def test_client_admin_cannot_update_foreign_integration(self):
        self.assertFalse(
            IntegrationAccessService.can_update_integration(
                self.client_admin_a,
                self.integration_b,
            )
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_sees_no_integration(self):
        self.assertFalse(
            IntegrationAccessService
            .get_accessible_integrations(
                self.project_manager
            )
            .exists()
        )

    def test_project_manager_has_no_assignable_environment(self):
        self.assertFalse(
            IntegrationAccessService
            .get_assignable_environments(
                self.project_manager
            )
            .exists()
        )

    def test_project_manager_cannot_create_or_update(self):
        self.assertFalse(
            IntegrationAccessService.can_create_integration(
                self.project_manager
            )
        )

        self.assertFalse(
            IntegrationAccessService.can_update_integration(
                self.project_manager,
                self.integration_a,
            )
        )

    # ------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_sees_no_integration(self):
        self.assertFalse(
            IntegrationAccessService
            .get_accessible_integrations(
                self.standard_user
            )
            .exists()
        )

    def test_standard_user_has_no_assignable_environment(self):
        self.assertFalse(
            IntegrationAccessService
            .get_assignable_environments(
                self.standard_user
            )
            .exists()
        )

    def test_standard_user_cannot_create_or_update(self):
        self.assertFalse(
            IntegrationAccessService.can_create_integration(
                self.standard_user
            )
        )

        self.assertFalse(
            IntegrationAccessService.can_update_integration(
                self.standard_user,
                self.integration_a,
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
            IntegrationAccessService
            .get_accessible_integrations(
                self.system_admin
            )
            .exists()
        )

        self.assertFalse(
            IntegrationAccessService
            .get_assignable_environments(
                self.system_admin
            )
            .exists()
        )

        self.assertFalse(
            IntegrationAccessService.can_create_integration(
                self.system_admin
            )
        )

        self.assertFalse(
            IntegrationAccessService.can_update_integration(
                self.system_admin,
                self.integration_a,
            )
        )