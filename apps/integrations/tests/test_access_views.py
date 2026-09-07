



from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment, ClientEnvironmentMembership
from apps.integrations.models import ExternalIntegration
from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


@override_settings(DEV_AUTO_LOGIN=False)
class ExternalIntegrationAccessViewTests(TestCase):
    """
    Tests HTTP du cloisonnement des intégrations externes.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Intégrations HTTP",
        )
        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Intégrations HTTP",
        )
        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Catalogues projet
        # --------------------------------------------------------------

        cls.project_status_catalog = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut projet",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_catalog,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.project_role_catalog = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôles projet",
        )

        cls.project_manager_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_catalog,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=10,
        )

        cls.access_level_catalog = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveaux d'accès",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_catalog,
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
            email="integration-http-system@example.com",
            first_name="System",
            last_name="Admin",
            is_system_admin=True,
        )

        cls.client_admin_a = User.objects.create(
            company=cls.company_a,
            email="integration-http-client-a@example.com",
            first_name="Client",
            last_name="Admin A",
        )

        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="integration-http-pm@example.com",
            first_name="Chef",
            last_name="Projet",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="integration-http-user@example.com",
            first_name="Utilisateur",
            last_name="Standard",
        )

        # --------------------------------------------------------------
        # Appartenances aux environnements clients
        # --------------------------------------------------------------

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin_a,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.project_manager,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.standard_user,
        )

        # --------------------------------------------------------------
        # Projet / rôle chef de projet
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-INT-HTTP-A",
            name="Projet intégrations HTTP A",
            status=cls.project_status,
        )

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.project_manager,
            role=cls.project_manager_role,
            access_level=cls.access_level,
            is_project_manager_responsible=True,
        )

        # --------------------------------------------------------------
        # Intégrations A / B
        # --------------------------------------------------------------

        cls.integration_a = ExternalIntegration.objects.create(
            client_environment=cls.environment_a,
            service_type=cls.service_type,
            provider=cls.provider,
            connection_status=cls.connection_status,
            code="HTTP-A",
            name="Intégration HTTP A",
            priority=100,
        )

        cls.integration_b = ExternalIntegration.objects.create(
            client_environment=cls.environment_b,
            service_type=cls.service_type,
            provider=cls.provider,
            connection_status=cls.connection_status,
            code="HTTP-B",
            name="Intégration HTTP B",
            priority=100,
        )

    def login(self, user):
        self.client.force_login(user)

    def valid_post_data(
        self,
        *,
        environment,
        code,
        name,
    ):
        return {
            "client_environment": str(environment.pk),
            "service_type": str(self.service_type.pk),
            "provider": str(self.provider.pk),
            "connection_status": str(
                self.connection_status.pk
            ),
            "code": code,
            "name": name,
            "priority": "100",
            "is_active": "on",
        }

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_list_sees_both_environments(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse("integrations:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.integration_a.name,
        )
        self.assertContains(
            response,
            self.integration_b.name,
        )

    def test_system_admin_create_form_contains_both_environments(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse("integrations:create")
        )

        self.assertEqual(response.status_code, 200)

        environment_queryset = (
            response.context["form"]
            .fields["client_environment"]
            .queryset
        )

        self.assertEqual(
            set(
                environment_queryset.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.environment_a.pk,
                self.environment_b.pk,
            },
        )

    def test_system_admin_can_update_foreign_environment(self):
        self.login(self.system_admin)

        response = self.client.get(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_b.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_list_only_sees_own_environment(self):
        self.login(self.client_admin_a)

        response = self.client.get(
            reverse("integrations:list")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            self.integration_a.name,
        )
        self.assertNotContains(
            response,
            self.integration_b.name,
        )

    def test_client_admin_create_form_only_contains_own_environment(self):
        self.login(self.client_admin_a)

        response = self.client.get(
            reverse("integrations:create")
        )

        self.assertEqual(response.status_code, 200)

        environment_queryset = (
            response.context["form"]
            .fields["client_environment"]
            .queryset
        )

        self.assertEqual(
            list(
                environment_queryset.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [self.environment_a.pk],
        )

    def test_client_admin_can_create_in_own_environment(self):
        self.login(self.client_admin_a)

        response = self.client.post(
            reverse("integrations:create"),
            data=self.valid_post_data(
                environment=self.environment_a,
                code="NEW-A",
                name="Nouvelle intégration A",
            ),
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            ExternalIntegration.objects.filter(
                client_environment=self.environment_a,
                code="NEW_A",
            ).exists()
        )
        
    def test_client_admin_cannot_forge_create_in_foreign_environment(self):
        self.login(self.client_admin_a)

        response = self.client.post(
            reverse("integrations:create"),
            data=self.valid_post_data(
                environment=self.environment_b,
                code="FORGED-B",
                name="Intégration forgée B",
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            ExternalIntegration.objects.filter(
                code="FORGED-B",
            ).exists()
        )

        self.assertIn(
            "client_environment",
            response.context["form"].errors,
        )

    def test_client_admin_can_update_own_integration(self):
        self.login(self.client_admin_a)

        response = self.client.get(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_a.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_client_admin_foreign_update_returns_404(self):
        self.login(self.client_admin_a)

        response = self.client.get(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_client_admin_cannot_forge_move_to_foreign_environment(self):
        self.login(self.client_admin_a)

        response = self.client.post(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_a.pk},
            ),
            data=self.valid_post_data(
                environment=self.environment_b,
                code=self.integration_a.code,
                name=self.integration_a.name,
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.integration_a.refresh_from_db()

        self.assertEqual(
            self.integration_a.client_environment,
            self.environment_a,
        )

        self.assertIn(
            "client_environment",
            response.context["form"].errors,
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_list_contains_no_integration(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse("integrations:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            self.integration_a.name,
        )
        self.assertNotContains(
            response,
            self.integration_b.name,
        )

    def test_project_manager_create_returns_403(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse("integrations:create")
        )

        self.assertEqual(response.status_code, 403)

    def test_project_manager_update_returns_404(self):
        self.login(self.project_manager)

        response = self.client.get(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_list_contains_no_integration(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse("integrations:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            self.integration_a.name,
        )
        self.assertNotContains(
            response,
            self.integration_b.name,
        )

    def test_standard_user_create_returns_403(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse("integrations:create")
        )

        self.assertEqual(response.status_code, 403)

    def test_standard_user_update_returns_404(self):
        self.login(self.standard_user)

        response = self.client.get(
            reverse(
                "integrations:update",
                kwargs={"pk": self.integration_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)