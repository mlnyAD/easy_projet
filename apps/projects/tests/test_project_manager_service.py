

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import Project, ProjectMembership
from apps.projects.services.project_manager import ProjectManagerService
from apps.users.models import User


class ProjectManagerServiceTests(TestCase):
    """
    Tests cibles du service d'accès aux chefs de projet.

    ProjectMembership constitue la source de vérité.

    Titulaire et délégués sont tous chefs de projet.
    La responsabilité ne modifie pas les droits.
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
            code="TEST_PROJECT_MANAGER_STATUS",
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
            reference="PM-SERVICE-001",
            name="Projet service chef de projet",
            company=cls.company,
            client_environment=cls.environment,
            status=cls.project_status,
        )

        cls.responsible_user = User.objects.create_user(
            email="pm.responsible.service@example.com",
            password="test-password",
            first_name="Alice",
            last_name="Responsable",
            company=cls.company,
        )

        cls.delegate_user = User.objects.create_user(
            email="pm.delegate.service@example.com",
            password="test-password",
            first_name="Bruno",
            last_name="Delegue",
            company=cls.company,
        )

        cls.standard_user = User.objects.create_user(
            email="standard.service@example.com",
            password="test-password",
            first_name="Claire",
            last_name="Utilisateur",
            company=cls.company,
        )

    def create_membership(
        self,
        *,
        user,
        role=None,
        responsible=False,
        active=True,
    ):
        return ProjectMembership.objects.create(
            project=self.project,
            user=user,
            role=role or self.project_manager_role,
            access_level=self.standard_access_level,
            is_project_manager_responsible=responsible,
            is_active=active,
        )

    def test_project_without_manager_returns_empty_queryset(self):
        memberships = (
            ProjectManagerService.get_project_managers(
                self.project
            )
        )

        self.assertEqual(memberships.count(), 0)

    def test_responsible_and_delegate_are_project_managers(self):
        responsible = self.create_membership(
            user=self.responsible_user,
            responsible=True,
        )

        delegate = self.create_membership(
            user=self.delegate_user,
        )

        memberships = list(
            ProjectManagerService.get_project_managers(
                self.project
            )
        )

        self.assertEqual(
            memberships,
            [
                responsible,
                delegate,
            ],
        )

    def test_responsible_manager_is_returned(self):
        self.create_membership(
            user=self.responsible_user,
            responsible=True,
        )

        self.create_membership(
            user=self.delegate_user,
        )

        result = (
            ProjectManagerService
            .get_responsible_project_manager(
                self.project
            )
        )

        self.assertEqual(
            result,
            self.responsible_user,
        )
    
    def test_project_without_responsible_returns_none(self):
        self.create_membership(
            user=self.delegate_user,
        )

        result = (
            ProjectManagerService
            .get_responsible_project_manager(
                self.project
            )
        )

        self.assertIsNone(result)

    def test_delegate_is_project_manager(self):
        self.create_membership(
            user=self.delegate_user,
        )

        self.assertTrue(
            ProjectManagerService.is_project_manager(
                user=self.delegate_user,
                project=self.project,
            )
        )

    def test_responsible_is_project_manager(self):
        self.create_membership(
            user=self.responsible_user,
            responsible=True,
        )

        self.assertTrue(
            ProjectManagerService.is_project_manager(
                user=self.responsible_user,
                project=self.project,
            )
        )

    def test_standard_project_member_is_not_project_manager(self):
        self.create_membership(
            user=self.standard_user,
            role=self.user_role,
        )

        self.assertFalse(
            ProjectManagerService.is_project_manager(
                user=self.standard_user,
                project=self.project,
            )
        )

    def test_inactive_project_manager_is_not_project_manager(self):
        self.create_membership(
            user=self.delegate_user,
            active=False,
        )

        self.assertFalse(
            ProjectManagerService.is_project_manager(
                user=self.delegate_user,
                project=self.project,
            )
        )

    def test_delegate_is_not_responsible(self):
        self.create_membership(
            user=self.delegate_user,
        )

        self.assertFalse(
            ProjectManagerService
            .is_responsible_project_manager(
                user=self.delegate_user,
                project=self.project,
            )
        )

    def test_responsible_manager_is_responsible(self):
        self.create_membership(
            user=self.responsible_user,
            responsible=True,
        )

        self.assertTrue(
            ProjectManagerService
            .is_responsible_project_manager(
                user=self.responsible_user,
                project=self.project,
            )
        )