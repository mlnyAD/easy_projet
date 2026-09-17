

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.users.models import User
from apps.users.services.access import UserAccessService


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class ClientEnvironmentMembershipViewTests(
    TestCase,
):
    @classmethod
    def setUpTestData(cls):
        cls.company_a = Company.objects.create(
            name="Société A",
        )

        cls.company_b = Company.objects.create(
            name="Société B",
        )

        cls.environment_a = (
            ClientEnvironment.objects.create(
                company=cls.company_a,
            )
        )

        cls.environment_b = (
            ClientEnvironment.objects.create(
                company=cls.company_b,
            )
        )

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="system-admin@example.com",
            first_name="Admin",
            last_name="Système",
            is_system_admin=True,
        )

        cls.target_user = User.objects.create(
            company=cls.company_a,
            email="target@example.com",
            first_name="Marie",
            last_name="Cible",
        )

        cls.foreign_user = User.objects.create(
            company=cls.company_b,
            email="foreign@example.com",
            first_name="Paul",
            last_name="Externe",
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="client-admin@example.com",
            first_name="Anne",
            last_name="Client",
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin,
            is_active=True,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_b,
            user=cls.foreign_user,
            is_active=True,
        )

    def setUp(self):
        self.client.force_login(
            self.system_admin
        )

    def get_list_url(
        self,
        user: User | None = None,
    ) -> str:
        return reverse(
            "users:client-environment-membership-list",
            kwargs={
                "user_pk": (
                    user or self.target_user
                ).pk,
            },
        )

    def get_create_url(
        self,
        user: User | None = None,
    ) -> str:
        return reverse(
            "users:client-environment-membership-create",
            kwargs={
                "user_pk": (
                    user or self.target_user
                ).pk,
            },
        )

    def test_system_admin_can_create_client_admin_membership(
        self,
    ):
        response = self.client.post(
            self.get_create_url(),
            {
                "client_environment": (
                    self.environment_b.pk
                ),
                "employment_type": "",
                "is_active": "on",
                "is_client_admin": "on",
                "is_client_admin_responsible": "on",
            },
        )

        self.assertRedirects(
            response,
            self.get_list_url(),
        )

        membership = (
            ClientEnvironmentMembership.objects.get(
                client_environment=self.environment_b,
                user=self.target_user,
            )
        )

        self.assertTrue(
            membership.is_active
        )

        self.assertTrue(
            membership.is_client_admin
        )

        self.assertTrue(
            membership.is_client_admin_responsible
        )

    def test_client_admin_membership_makes_user_visible_and_authorized(
        self,
    ):
        ClientEnvironmentMembership.objects.create(
            client_environment=self.environment_a,
            user=self.target_user,
            is_active=True,
            is_client_admin=True,
            is_client_admin_responsible=False,
        )

        self.client.force_login(
            self.target_user
        )

        self.assertTrue(
            UserAccessService.can_create_user(
                self.target_user
            )
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
            self.target_user.email,
        )

    def test_client_admin_cannot_open_foreign_user_memberships(
        self,
    ):
        self.client.force_login(
            self.client_admin
        )

        response = self.client.get(
            self.get_list_url(
                self.foreign_user
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )