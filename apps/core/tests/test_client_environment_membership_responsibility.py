

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.users.models import User


class ClientEnvironmentMembershipResponsibilityTests(TestCase):
    """
    Tests cibles de la responsabilité d'administration client.

    Le titulaire et les administrateurs délégués possèdent la même
    fonction d'administration. La qualité de titulaire est uniquement
    organisationnelle.

    Un environnement peut temporairement ne posséder aucun titulaire.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société cliente",
        )

        cls.environment = ClientEnvironment.objects.create(
            company=cls.company,
        )

        cls.responsible_user = User.objects.create_user(
            email="responsible@example.com",
            password="test-password",
            first_name="Alice",
            last_name="Responsable",
            company=cls.company,
        )

        cls.delegate_user = User.objects.create_user(
            email="delegate@example.com",
            password="test-password",
            first_name="Bruno",
            last_name="Delegue",
            company=cls.company,
        )

        cls.second_delegate_user = User.objects.create_user(
            email="delegate2@example.com",
            password="test-password",
            first_name="Claire",
            last_name="Delegue",
            company=cls.company,
        )

    def test_environment_can_have_no_responsible_admin(self):
        membership = ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.delegate_user,
            is_client_admin=True,
            is_client_admin_responsible=False,
        )

        self.assertTrue(membership.is_client_admin)
        self.assertFalse(
            membership.is_client_admin_responsible
        )

    def test_environment_can_have_one_responsible_admin(self):
        membership = ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.responsible_user,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        self.assertTrue(membership.is_client_admin)
        self.assertTrue(
            membership.is_client_admin_responsible
        )

    def test_environment_can_have_multiple_delegate_admins(self):
        ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.delegate_user,
            is_client_admin=True,
            is_client_admin_responsible=False,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.second_delegate_user,
            is_client_admin=True,
            is_client_admin_responsible=False,
        )

        admin_count = (
            ClientEnvironmentMembership.objects
            .filter(
                client_environment=self.environment,
                is_client_admin=True,
                is_active=True,
            )
            .count()
        )

        self.assertEqual(admin_count, 2)

    def test_second_active_responsible_admin_is_rejected_by_database(
        self,
    ):
        ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.responsible_user,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClientEnvironmentMembership.objects.create(
                    client_environment=self.environment,
                    user=self.delegate_user,
                    is_client_admin=True,
                    is_client_admin_responsible=True,
                )

    def test_new_responsible_is_allowed_after_previous_is_deactivated(
        self,
    ):
        previous = ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.responsible_user,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        previous.is_active = False
        previous.save(update_fields=["is_active"])

        replacement = ClientEnvironmentMembership.objects.create(
            client_environment=self.environment,
            user=self.delegate_user,
            is_client_admin=True,
            is_client_admin_responsible=True,
        )

        self.assertTrue(replacement.is_active)
        self.assertTrue(
            replacement.is_client_admin_responsible
        )

    def test_responsible_must_be_client_admin(self):
        membership = ClientEnvironmentMembership(
            client_environment=self.environment,
            user=self.responsible_user,
            is_client_admin=False,
            is_client_admin_responsible=True,
        )

        with self.assertRaises(ValidationError) as context:
            membership.full_clean()

        self.assertIn(
            "is_client_admin_responsible",
            context.exception.message_dict,
        )