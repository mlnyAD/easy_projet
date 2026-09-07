

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import Project, ProjectMembership
from apps.users.models import User
from apps.users.services import TemporaryPasswordService


class UserAccessViewTests(TestCase):
    """
    Tests HTTP des règles d'accès aux utilisateurs.

    Architecture Level 2 :

    - SYSTEM_ADMIN est porté par User.is_system_admin ;
    - CLIENT_ADMIN est porté par ClientEnvironmentMembership ;
    - PROJECT_MANAGER est porté par ProjectMembership ;
    - le niveau d'accès projet est porté par ProjectMembership ;
    - Company représente l'employeur et ne constitue pas
      un périmètre d'autorisation ;
    - la visibilité d'un utilisateur dépend des environnements
      clients accessibles à l'acteur.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Users HTTP",
            is_active=True,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Users HTTP",
            is_active=True,
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
            is_active=True,
        )

        cls.project_status = cls._catalog_value(
            cls.project_status_type,
            "IN_PROGRESS",
            "En cours",
        )

        # --------------------------------------------------------------
        # Rôles projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôles projet",
            is_active=True,
        )

        cls.project_manager_role = cls._catalog_value(
            cls.project_role_type,
            "PROJECT_MANAGER",
            "Chef de projet",
        )

        # --------------------------------------------------------------
        # Niveau d'accès projet
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveaux d'accès",
            is_active=True,
        )

        cls.access_level = cls._catalog_value(
            cls.access_level_type,
            "STANDARD",
            "Standard",
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = cls._create_user(
            email="system.users.http@example.com",
            company=cls.company_a,
            is_system_admin=True,
        )

        cls.client_admin_a = cls._create_user(
            email="admin.a.users.http@example.com",
            company=cls.company_a,
        )

        cls.project_manager = cls._create_user(
            email="pm.users.http@example.com",
            company=cls.company_a,
        )

        cls.standard_user = cls._create_user(
            email="standard.users.http@example.com",
            company=cls.company_a,
        )

        cls.target_a = cls._create_user(
            email="target.a.users.http@example.com",
            company=cls.company_a,
        )

        cls.target_b = cls._create_user(
            email="target.b.users.http@example.com",
            company=cls.company_b,
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

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.target_a,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_b,
            user=cls.target_b,
        )

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-USERS-HTTP-A",
            name="Projet Users HTTP A",
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

    @classmethod
    def _catalog_value(
        cls,
        catalog_type,
        code,
        label,
    ):
        return CatalogValue.objects.create(
            catalog_type=catalog_type,
            code=code,
            label=label,
            is_active=True,
        )

    @classmethod
    def _create_user(
        cls,
        *,
        email,
        company,
        is_system_admin=False,
    ):
        user = User.objects.create(
            email=email,
            first_name="Test",
            last_name=email.split("@")[0],
            company=company,
            is_system_admin=is_system_admin,
            is_active=True,
        )

        user.set_password("TestPassword123!")
        user.save()

        return user

    def _form_data(
        self,
        *,
        email,
        company,
    ):
        return {
            "last_name": "DUPONT",
            "first_name": "Jean",
            "email": email,
            "phone": "",
            "mobile": "",
            "company": company.pk,
            "job": "",
            "is_active": True,
        }

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_list_contains_both_companies(self):
        self.client.force_login(
            self.system_admin
        )

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.target_a.email,
        )

        self.assertContains(
            response,
            self.target_b.email,
        )

    def test_system_admin_create_form_contains_both_companies(self):
        self.client.force_login(
            self.system_admin
        )

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        queryset = response.context["form"].fields[
            "company"
        ].queryset

        self.assertIn(
            self.company_a,
            queryset,
        )

        self.assertIn(
            self.company_b,
            queryset,
        )

    def test_system_admin_can_update_foreign_company_user(self):
        self.client.force_login(
            self.system_admin
        )

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_b.pk,
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

    def test_client_admin_list_contains_administered_environment_users(
        self,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.target_a.email,
        )

        self.assertNotContains(
            response,
            self.target_b.email,
        )

    def test_client_admin_create_form_contains_all_active_companies(
        self,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        queryset = response.context["form"].fields[
            "company"
        ].queryset

        self.assertIn(
            self.company_a,
            queryset,
        )

        self.assertIn(
            self.company_b,
            queryset,
        )

    @patch.object(
        TemporaryPasswordService,
        "reset_and_send",
    )
    def test_client_admin_can_create_user_with_own_company(
        self,
        reset_and_send,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.post(
            reverse("users:create"),
            data=self._form_data(
                email="new.a@example.com",
                company=self.company_a,
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            User.objects.filter(
                email="new.a@example.com",
                company=self.company_a,
            ).exists()
        )

        reset_and_send.assert_called_once()

    @patch.object(
        TemporaryPasswordService,
        "reset_and_send",
    )
    def test_client_admin_can_create_user_with_foreign_employer(
        self,
        reset_and_send,
    ):
        """
        Company représente l'employeur.

        Un administrateur client autorisé à créer
        un compte peut sélectionner toute société active.
        """

        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.post(
            reverse("users:create"),
            data=self._form_data(
                email="new.b@example.com",
                company=self.company_b,
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            User.objects.filter(
                email="new.b@example.com",
                company=self.company_b,
            ).exists()
        )

        reset_and_send.assert_called_once()

    def test_client_admin_can_update_user_in_administered_environment(
        self,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_client_admin_cannot_open_user_outside_administered_environment(
        self,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_client_admin_can_change_employer_to_active_company(
        self,
    ):
        """
        Le changement d'employeur ne modifie pas
        le périmètre d'autorisation du compte.
        """

        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.post(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_a.pk,
                },
            ),
            data=self._form_data(
                email=self.target_a.email,
                company=self.company_b,
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.target_a.refresh_from_db()

        self.assertEqual(
            self.target_a.company_id,
            self.company_b.pk,
        )

    @patch.object(
        TemporaryPasswordService,
        "reset_and_send",
    )
    def test_client_admin_cannot_resend_password_outside_environment(
        self,
        reset_and_send,
    ):
        self.client.force_login(
            self.client_admin_a
        )

        response = self.client.post(
            reverse(
                "users:temporary-password-resend",
                kwargs={
                    "pk": self.target_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        reset_and_send.assert_not_called()

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_list_contains_environment_users(self):
        self.client.force_login(
            self.project_manager
        )

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.target_a.email,
        )

        self.assertNotContains(
            response,
            self.target_b.email,
        )

    def test_project_manager_create_is_forbidden(self):
        self.client.force_login(
            self.project_manager
        )

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_project_manager_update_is_hidden(self):
        self.client.force_login(
            self.project_manager
        )

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # USER SANS PROJET
    # ------------------------------------------------------------------

    def test_standard_user_without_project_list_is_empty(self):
        self.client.force_login(
            self.standard_user
        )

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            self.target_a.email,
        )

        self.assertNotContains(
            response,
            self.target_b.email,
        )

    def test_standard_user_create_is_forbidden(self):
        self.client.force_login(
            self.standard_user
        )

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_standard_user_update_is_hidden(self):
        self.client.force_login(
            self.standard_user
        )

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={
                    "pk": self.target_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )