

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.users.models import User
from apps.users.services.access import UserAccessService


class UserAccessServiceTests(TestCase):
    """
    Tests de la politique d'accès à l'administration utilisateurs.

    Architecture Level 2 :

    - SYSTEM_ADMIN est porté par User.is_system_admin ;
    - CLIENT_ADMIN est porté par ClientEnvironmentMembership ;
    - PROJECT_MANAGER est porté par ProjectMembership ;
    - la société de l'utilisateur représente son employeur
      et ne constitue pas un périmètre d'autorisation ;
    - la visibilité d'un utilisateur dépend des environnements
      clients accessibles à l'acteur.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Users",
        )

        cls.company_b = Company.objects.create(
            name="Société B - Users",
        )

        # --------------------------------------------------------------
        # Environnements clients
        # --------------------------------------------------------------

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut projet",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Rôles projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle sur projet",
        )

        cls.project_manager_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Niveau d'accès projet
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="users-system@example.com",
            first_name="System",
            last_name="Admin",
            is_system_admin=True,
        )

        cls.client_admin_a = User.objects.create(
            company=cls.company_a,
            email="users-client-a@example.com",
            first_name="Client",
            last_name="Admin A",
        )

        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="users-pm@example.com",
            first_name="Chef",
            last_name="Projet",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="users-standard@example.com",
            first_name="Utilisateur",
            last_name="Standard",
        )

        # --------------------------------------------------------------
        # Utilisateurs cibles
        #
        # target_a et target_b appartiennent volontairement
        # à des employeurs différents et à des environnements
        # clients différents.
        # --------------------------------------------------------------

        cls.target_a = User.objects.create(
            company=cls.company_a,
            email="target-a@example.com",
            first_name="Cible",
            last_name="A",
        )

        cls.target_b = User.objects.create(
            company=cls.company_b,
            email="target-b@example.com",
            first_name="Cible",
            last_name="B",
        )

        # --------------------------------------------------------------
        # Appartenance aux environnements clients
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

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.target_a,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_b,
            user=cls.target_b,
        )

        # --------------------------------------------------------------
        # Projet de l'environnement A
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-USERS-A",
            name="Projet Users A",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Chef de projet
        # --------------------------------------------------------------

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.project_manager,
            role=cls.project_manager_role,
            access_level=cls.access_level,
            is_project_manager_responsible=True,
        )

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_sees_all_users(self):
        user_ids = set(
            UserAccessService
            .get_accessible_users(
                self.system_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.target_a.pk,
            user_ids,
        )

        self.assertIn(
            self.target_b.pk,
            user_ids,
        )

    def test_system_admin_can_assign_all_active_companies(self):
        company_ids = set(
            UserAccessService
            .get_assignable_companies(
                self.system_admin
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            company_ids,
            {
                self.company_a.pk,
                self.company_b.pk,
            },
        )

    def test_system_admin_can_create_update_and_reset(self):
        self.assertTrue(
            UserAccessService.can_create_user(
                self.system_admin
            )
        )

        self.assertTrue(
            UserAccessService.can_update_user(
                self.system_admin,
                self.target_b,
            )
        )

        self.assertTrue(
            UserAccessService.can_reset_temporary_password(
                self.system_admin,
                self.target_b,
            )
        )

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_sees_users_known_in_administered_environment(self):
        user_ids = set(
            UserAccessService
            .get_accessible_users(
                self.client_admin_a
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.target_a.pk,
            user_ids,
        )

        self.assertNotIn(
            self.target_b.pk,
            user_ids,
        )

    def test_client_admin_can_assign_all_active_companies(self):
        company_ids = set(
            UserAccessService
            .get_assignable_companies(
                self.client_admin_a
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertEqual(
            company_ids,
            {
                self.company_a.pk,
                self.company_b.pk,
            },
        )

    def test_client_admin_can_create_user(self):
        self.assertTrue(
            UserAccessService.can_create_user(
                self.client_admin_a
            )
        )

    def test_client_admin_can_update_user_known_in_administered_environment(
        self,
    ):
        self.assertTrue(
            UserAccessService.can_update_user(
                self.client_admin_a,
                self.target_a,
            )
        )

    def test_client_admin_cannot_update_user_outside_administered_environment(
        self,
    ):
        self.assertFalse(
            UserAccessService.can_update_user(
                self.client_admin_a,
                self.target_b,
            )
        )

    def test_client_admin_can_reset_user_known_in_administered_environment(
        self,
    ):
        self.assertTrue(
            UserAccessService.can_reset_temporary_password(
                self.client_admin_a,
                self.target_a,
            )
        )

    def test_client_admin_cannot_reset_user_outside_administered_environment(
        self,
    ):
        self.assertFalse(
            UserAccessService.can_reset_temporary_password(
                self.client_admin_a,
                self.target_b,
            )
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_has_visibility_but_no_global_admin_access(
        self,
    ):
        user_ids = set(
            UserAccessService
            .get_accessible_users(
                self.project_manager
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.target_a.pk,
            user_ids,
        )

        self.assertNotIn(
            self.target_b.pk,
            user_ids,
        )

        self.assertFalse(
            UserAccessService
            .get_assignable_companies(
                self.project_manager
            )
            .exists()
        )

        self.assertFalse(
            UserAccessService.can_create_user(
                self.project_manager
            )
        )

        self.assertFalse(
            UserAccessService.can_update_user(
                self.project_manager,
                self.target_a,
            )
        )

        self.assertFalse(
            UserAccessService.can_reset_temporary_password(
                self.project_manager,
                self.target_a,
            )
        )

    # ------------------------------------------------------------------
    # USER SANS PROJET
    # ------------------------------------------------------------------

    def test_standard_user_without_project_can_view_own_environment(
        self,
    ):
        accessible_users = (
            UserAccessService
            .get_accessible_users(
                self.standard_user
            )
        )

        self.assertTrue(
            accessible_users.filter(
                pk=self.standard_user.pk,
            ).exists()
        )

        self.assertTrue(
            accessible_users.filter(
                pk=self.target_a.pk,
            ).exists()
        )

        self.assertFalse(
            accessible_users.filter(
                pk=self.target_b.pk,
            ).exists()
        )

        self.assertFalse(
            UserAccessService
            .get_assignable_companies(
                self.standard_user
            )
            .exists()
        )

        self.assertFalse(
            UserAccessService.can_create_user(
                self.standard_user
            )
        )

        self.assertFalse(
            UserAccessService.can_update_user(
                self.standard_user,
                self.target_a,
            )
        )

        self.assertFalse(
            UserAccessService.can_reset_temporary_password(
                self.standard_user,
                self.target_a,
            )
        )
        
    # ------------------------------------------------------------------
    # Inactif
    # ------------------------------------------------------------------

    def test_inactive_system_admin_has_no_access(self):
        self.system_admin.is_active = False
        self.system_admin.save(
            update_fields=["is_active"]
        )

        self.assertFalse(
            UserAccessService
            .get_accessible_users(
                self.system_admin
            )
            .exists()
        )

        self.assertFalse(
            UserAccessService
            .get_assignable_companies(
                self.system_admin
            )
            .exists()
        )

        self.assertFalse(
            UserAccessService.can_create_user(
                self.system_admin
            )
        )

        self.assertFalse(
            UserAccessService.can_update_user(
                self.system_admin,
                self.target_a,
            )
        )