

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


class ProjectMembershipResponsibilityTests(TestCase):
    """
    Tests cibles de la responsabilité de chef de projet.

    Tous les membres ayant le rôle PROJECT_MANAGER disposent de la
    fonction de chef de projet.

    La qualité de titulaire est uniquement organisationnelle et ne
    modifie pas le périmètre d'autorisation.

    Un projet peut temporairement ne posséder aucun titulaire.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société projet",
        )

        cls.environment = ClientEnvironment.objects.create(
            company=cls.company,
        )

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_PROJECT_STATUS",
            label="Statut projet test",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="ACTIVE",
            label="Actif",
        )

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle projet",
        )

        cls.project_manager_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
        )

        cls.user_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="USER",
            label="Utilisateur",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès projet",
        )

        cls.standard_access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
        )

        cls.project = Project.objects.create(
            reference="RESP-001",
            name="Projet responsabilité",
            company=cls.company,
            client_environment=cls.environment,
            status=cls.project_status,
        )

        cls.responsible_user = User.objects.create_user(
            email="pm.responsible@example.com",
            password="test-password",
            first_name="Alice",
            last_name="Responsable",
            company=cls.company,
        )

        cls.delegate_user = User.objects.create_user(
            email="pm.delegate@example.com",
            password="test-password",
            first_name="Bruno",
            last_name="Delegue",
            company=cls.company,
        )

        cls.second_delegate_user = User.objects.create_user(
            email="pm.delegate2@example.com",
            password="test-password",
            first_name="Claire",
            last_name="Delegue",
            company=cls.company,
        )

        cls.standard_user = User.objects.create_user(
            email="user@example.com",
            password="test-password",
            first_name="David",
            last_name="Utilisateur",
            company=cls.company,
        )

    def create_project_manager_membership(
        self,
        *,
        user,
        responsible=False,
        active=True,
    ):
        return ProjectMembership.objects.create(
            project=self.project,
            user=user,
            role=self.project_manager_role,
            access_level=self.standard_access_level,
            is_project_manager_responsible=responsible,
            is_active=active,
        )

    def test_project_can_have_no_responsible_project_manager(self):
        membership = self.create_project_manager_membership(
            user=self.delegate_user,
            responsible=False,
        )

        self.assertEqual(
            membership.role,
            self.project_manager_role,
        )
        self.assertFalse(
            membership.is_project_manager_responsible
        )

    def test_project_can_have_one_responsible_project_manager(self):
        membership = self.create_project_manager_membership(
            user=self.responsible_user,
            responsible=True,
        )

        self.assertEqual(
            membership.role,
            self.project_manager_role,
        )
        self.assertTrue(
            membership.is_project_manager_responsible
        )

    def test_project_can_have_multiple_delegate_project_managers(
        self,
    ):
        self.create_project_manager_membership(
            user=self.delegate_user,
        )

        self.create_project_manager_membership(
            user=self.second_delegate_user,
        )

        manager_count = (
            ProjectMembership.objects
            .filter(
                project=self.project,
                role=self.project_manager_role,
                is_active=True,
            )
            .count()
        )

        self.assertEqual(manager_count, 2)

    def test_second_active_responsible_is_rejected_by_database(
        self,
    ):
        self.create_project_manager_membership(
            user=self.responsible_user,
            responsible=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_project_manager_membership(
                    user=self.delegate_user,
                    responsible=True,
                )

    def test_new_responsible_is_allowed_after_previous_is_deactivated(
        self,
    ):
        previous = self.create_project_manager_membership(
            user=self.responsible_user,
            responsible=True,
        )

        previous.is_active = False
        previous.save(update_fields=["is_active"])

        replacement = self.create_project_manager_membership(
            user=self.delegate_user,
            responsible=True,
        )

        self.assertTrue(replacement.is_active)
        self.assertTrue(
            replacement.is_project_manager_responsible
        )

    def test_responsible_must_have_project_manager_role(self):
        membership = ProjectMembership(
            project=self.project,
            user=self.standard_user,
            role=self.user_role,
            access_level=self.standard_access_level,
            is_project_manager_responsible=True,
        )

        with self.assertRaises(ValidationError) as context:
            membership.full_clean()

        self.assertIn(
            "is_project_manager_responsible",
            context.exception.message_dict,
        )