

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.users.models import User
from apps.users.services import TemporaryPasswordService


class UserAccessViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company_a = Company.objects.create(
            name="Société A - Users HTTP",
            is_active=True,
        )
        cls.company_b = Company.objects.create(
            name="Société B - Users HTTP",
            is_active=True,
        )

        cls.global_role_type = CatalogType.objects.create(
            code="USER_GLOBAL_ROLE",
            label="Rôles globaux",
            is_active=True,
        )
        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveaux d'accès",
            is_active=True,
        )

        cls.system_admin_role = cls._catalog_value(
            cls.global_role_type,
            "SYSTEM_ADMIN",
            "Administrateur système",
        )
        cls.client_admin_role = cls._catalog_value(
            cls.global_role_type,
            "CLIENT_ADMIN",
            "Administrateur client",
        )
        cls.project_manager_role = cls._catalog_value(
            cls.global_role_type,
            "PROJECT_MANAGER",
            "Chef de projet",
        )
        cls.user_role = cls._catalog_value(
            cls.global_role_type,
            "USER",
            "Utilisateur",
        )

        cls.access_level = cls._catalog_value(
            cls.access_level_type,
            "STANDARD",
            "Standard",
        )

        cls.system_admin = cls._create_user(
            email="system.users.http@example.com",
            company=cls.company_a,
            role=cls.system_admin_role,
        )
        cls.client_admin_a = cls._create_user(
            email="admin.a.users.http@example.com",
            company=cls.company_a,
            role=cls.client_admin_role,
        )
        cls.project_manager = cls._create_user(
            email="pm.users.http@example.com",
            company=cls.company_a,
            role=cls.project_manager_role,
        )
        cls.standard_user = cls._create_user(
            email="standard.users.http@example.com",
            company=cls.company_a,
            role=cls.user_role,
        )

        cls.target_a = cls._create_user(
            email="target.a.users.http@example.com",
            company=cls.company_a,
            role=cls.user_role,
        )
        cls.target_b = cls._create_user(
            email="target.b.users.http@example.com",
            company=cls.company_b,
            role=cls.user_role,
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
        role,
    ):
        user = User.objects.create(
            email=email,
            first_name="Test",
            last_name=email.split("@")[0],
            company=company,
            global_role=role,
            access_level=cls.access_level,
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
            "employment_type": "",
            "job": "",
            "global_role": self.user_role.pk,
            "access_level": self.access_level.pk,
            "is_active": True,
        }

    # ------------------------------------------------------------------
    # SYSTEM_ADMIN
    # ------------------------------------------------------------------

    def test_system_admin_list_contains_both_companies(self):
        self.client.force_login(self.system_admin)

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.target_a.email)
        self.assertContains(response, self.target_b.email)

    def test_system_admin_create_form_contains_both_companies(self):
        self.client.force_login(self.system_admin)

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(response.status_code, 200)

        queryset = response.context["form"].fields[
            "company"
        ].queryset

        self.assertIn(self.company_a, queryset)
        self.assertIn(self.company_b, queryset)

    def test_system_admin_can_update_foreign_company_user(self):
        self.client.force_login(self.system_admin)

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={"pk": self.target_b.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # CLIENT_ADMIN
    # ------------------------------------------------------------------

    def test_client_admin_list_only_contains_own_company(self):
        self.client.force_login(self.client_admin_a)

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.target_a.email)
        self.assertNotContains(response, self.target_b.email)

    def test_client_admin_create_form_only_contains_own_company(self):
        self.client.force_login(self.client_admin_a)

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(response.status_code, 200)

        queryset = response.context["form"].fields[
            "company"
        ].queryset

        self.assertIn(self.company_a, queryset)
        self.assertNotIn(self.company_b, queryset)

    @patch.object(
        TemporaryPasswordService,
        "reset_and_send",
    )
    def test_client_admin_can_create_in_own_company(
        self,
        reset_and_send,
    ):
        self.client.force_login(self.client_admin_a)

        response = self.client.post(
            reverse("users:create"),
            data=self._form_data(
                email="new.a@example.com",
                company=self.company_a,
            ),
        )

        self.assertEqual(response.status_code, 302)

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
    def test_client_admin_cannot_create_in_foreign_company(
        self,
        reset_and_send,
    ):
        self.client.force_login(self.client_admin_a)

        response = self.client.post(
            reverse("users:create"),
            data=self._form_data(
                email="new.b@example.com",
                company=self.company_b,
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            User.objects.filter(
                email="new.b@example.com",
            ).exists()
        )

        reset_and_send.assert_not_called()

    def test_client_admin_can_update_own_company_user(self):
        self.client.force_login(self.client_admin_a)

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={"pk": self.target_a.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_client_admin_cannot_open_foreign_user(self):
        self.client.force_login(self.client_admin_a)

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={"pk": self.target_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_client_admin_cannot_move_user_to_foreign_company(self):
        self.client.force_login(self.client_admin_a)

        response = self.client.post(
            reverse(
                "users:update",
                kwargs={"pk": self.target_a.pk},
            ),
            data=self._form_data(
                email=self.target_a.email,
                company=self.company_b,
            ),
        )

        self.assertEqual(response.status_code, 200)

        self.target_a.refresh_from_db()

        self.assertEqual(
            self.target_a.company_id,
            self.company_a.pk,
        )

    @patch.object(
        TemporaryPasswordService,
        "reset_and_send",
    )
    def test_client_admin_cannot_resend_foreign_password(
        self,
        reset_and_send,
    ):
        self.client.force_login(self.client_admin_a)

        response = self.client.post(
            reverse(
                "users:temporary-password-resend",
                kwargs={"pk": self.target_b.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
        reset_and_send.assert_not_called()

    # ------------------------------------------------------------------
    # PROJECT_MANAGER
    # ------------------------------------------------------------------

    def test_project_manager_list_is_empty(self):
        self.client.force_login(self.project_manager)

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.target_a.email)
        self.assertNotContains(response, self.target_b.email)

    def test_project_manager_create_is_forbidden(self):
        self.client.force_login(self.project_manager)

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(response.status_code, 403)

    def test_project_manager_update_is_hidden(self):
        self.client.force_login(self.project_manager)

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={"pk": self.target_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------------------------------
    # USER
    # ------------------------------------------------------------------

    def test_standard_user_list_is_empty(self):
        self.client.force_login(self.standard_user)

        response = self.client.get(
            reverse("users:list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.target_a.email)
        self.assertNotContains(response, self.target_b.email)

    def test_standard_user_create_is_forbidden(self):
        self.client.force_login(self.standard_user)

        response = self.client.get(
            reverse("users:create")
        )

        self.assertEqual(response.status_code, 403)

    def test_standard_user_update_is_hidden(self):
        self.client.force_login(self.standard_user)

        response = self.client.get(
            reverse(
                "users:update",
                kwargs={"pk": self.target_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)