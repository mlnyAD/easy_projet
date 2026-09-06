

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.users.models import User
from apps.users.services.access import UserAccessService


class UserAccessServiceTests(TestCase):
    """
    Tests de la politique d'accès à l'administration utilisateurs.
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
            code="TEST_USER_ACCESS_LEVEL",
            label="Niveau accès test utilisateurs",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs administrateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="users-system@example.com",
            first_name="System",
            last_name="Admin",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        cls.client_admin_a = User.objects.create(
            company=cls.company_a,
            email="users-client-a@example.com",
            first_name="Client",
            last_name="Admin A",
            global_role=cls.client_admin_role,
            access_level=cls.access_level,
        )

        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="users-pm@example.com",
            first_name="Chef",
            last_name="Projet",
            global_role=cls.project_manager_role,
            access_level=cls.access_level,
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="users-standard@example.com",
            first_name="Utilisateur",
            last_name="Standard",
            global_role=cls.user_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Utilisateurs cibles A / B
        # --------------------------------------------------------------

        cls.target_a = User.objects.create(
            company=cls.company_a,
            email="target-a@example.com",
            first_name="Cible",
            last_name="A",
            global_role=cls.user_role,
            access_level=cls.access_level,
        )

        cls.target_b = User.objects.create(
            company=cls.company_b,
            email="target-b@example.com",
            first_name="Cible",
            last_name="B",
            global_role=cls.user_role,
            access_level=cls.access_level,
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

    def test_client_admin_only_sees_own_company_users(self):
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

    def test_client_admin_only_assigns_own_company(self):
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
            },
        )

    def test_client_admin_can_create_user(self):
        self.assertTrue(
            UserAccessService.can_create_user(
                self.client_admin_a
            )
        )

    def test_client_admin_can_update_own_company_user(self):
        self.assertTrue(
            UserAccessService.can_update_user(
                self.client_admin_a,
                self.target_a,
            )
        )

    def test_client_admin_cannot_update_foreign_user(self):
        self.assertFalse(
            UserAccessService.can_update_user(
                self.client_admin_a,
                self.target_b,
            )
        )

    def test_client_admin_can_reset_own_company_user(self):
        self.assertTrue(
            UserAccessService.can_reset_temporary_password(
                self.client_admin_a,
                self.target_a,
            )
        )

    def test_client_admin_cannot_reset_foreign_user(self):
        self.assertFalse(
            UserAccessService.can_reset_temporary_password(
                self.client_admin_a,
                self.target_b,
            )
        )

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_has_no_admin_access(self):
        self.assertFalse(
            UserAccessService
            .get_accessible_users(
                self.project_manager
            )
            .exists()
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
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_has_no_admin_access(self):
        self.assertFalse(
            UserAccessService
            .get_accessible_users(
                self.standard_user
            )
            .exists()
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