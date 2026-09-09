

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import Project, ProjectMembership
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
from apps.users.models import User


class ProjectAuthorizationServiceTests(TestCase):
    """
    Tests des autorisations projet Niveau 2.

    La visibilité d'un projet et les droits d'action sur ce projet
    sont deux notions distinctes.

    Matrice cible :
    - administrateur système :
      consultation, travail, administration, financier ;
    - administrateur client de l'environnement :
      consultation, travail, administration, financier ;
    - chef de projet du projet, titulaire ou délégué :
      consultation, travail, administration, financier ;
    - chef de projet transverse :
      consultation uniquement ;
    - membre STANDARD :
      consultation et travail ;
    - membre READ_ONLY :
      consultation uniquement ;
    - utilisateur sans périmètre :
      aucun droit.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés et environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société cliente A",
        )

        cls.company_b = Company.objects.create(
            name="Société cliente B",
        )

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
            label="Rôle projet",
        )

        cls.project_user_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.project_manager_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Niveaux d'accès projet
        # --------------------------------------------------------------

        cls.project_access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès projet",
        )

        cls.standard_access = CatalogValue.objects.create(
            catalog_type=cls.project_access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
            is_default=True,
        )

        cls.read_only_access = CatalogValue.objects.create(
            catalog_type=cls.project_access_level_type,
            code="READ_ONLY",
            label="Lecture seule",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project_a1 = Project.objects.create(
            company=cls.company_a,
            reference="A-001",
            name="Projet A1",
            status=cls.project_status,
        )

        cls.project_a2 = Project.objects.create(
            company=cls.company_a,
            reference="A-002",
            name="Projet A2",
            status=cls.project_status,
        )

        cls.project_b1 = Project.objects.create(
            company=cls.company_b,
            reference="B-001",
            name="Projet B1",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="system-admin-auth@example.com",
            first_name="Admin",
            last_name="Système",
            is_system_admin=True,
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="client-admin-auth@example.com",
            first_name="Admin",
            last_name="Client",
        )

        cls.responsible_project_manager = User.objects.create(
            company=cls.company_a,
            email="responsible-pm-auth@example.com",
            first_name="Chef",
            last_name="Projet titulaire",
        )

        cls.delegate_project_manager = User.objects.create(
            company=cls.company_a,
            email="delegate-pm-auth@example.com",
            first_name="Chef",
            last_name="Projet délégué",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="standard-auth@example.com",
            first_name="Utilisateur",
            last_name="Standard",
        )

        cls.read_only_user = User.objects.create(
            company=cls.company_a,
            email="readonly-auth@example.com",
            first_name="Utilisateur",
            last_name="Lecture seule",
        )

        cls.outsider = User.objects.create(
            company=cls.company_b,
            email="outsider-auth@example.com",
            first_name="Utilisateur",
            last_name="Extérieur",
        )

        cls.inactive_system_admin = User.objects.create(
            company=cls.company_a,
            email="inactive-system-admin-auth@example.com",
            first_name="Admin",
            last_name="Système inactif",
            is_system_admin=True,
            is_active=False,
        )

        # --------------------------------------------------------------
        # Administration client
        # --------------------------------------------------------------

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin,
            is_client_admin=True,
            is_active=True,
        )

        # --------------------------------------------------------------
        # Participations projet
        # --------------------------------------------------------------

        ProjectMembership.objects.create(
            project=cls.project_a1,
            user=cls.responsible_project_manager,
            role=cls.project_manager_role,
            access_level=cls.standard_access,
            is_project_manager_responsible=True,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_a1,
            user=cls.delegate_project_manager,
            role=cls.project_manager_role,
            access_level=cls.standard_access,
            is_project_manager_responsible=False,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_a1,
            user=cls.standard_user,
            role=cls.project_user_role,
            access_level=cls.standard_access,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_a1,
            user=cls.read_only_user,
            role=cls.project_user_role,
            access_level=cls.read_only_access,
            is_active=True,
        )

    def assert_permissions(
        self,
        user,
        project,
        *,
        view,
        work,
        administer,
        financial,
    ):
        self.assertEqual(
            ProjectAuthorizationService.can_view_project(
                user=user,
                project=project,
            ),
            view,
        )

        self.assertEqual(
            ProjectAuthorizationService.can_work_on_project(
                user=user,
                project=project,
            ),
            work,
        )

        self.assertEqual(
            ProjectAuthorizationService.can_administer_project(
                user=user,
                project=project,
            ),
            administer,
        )

        self.assertEqual(
            ProjectAuthorizationService.can_access_financial_data(
                user=user,
                project=project,
            ),
            financial,
        )

    def test_system_admin_has_all_permissions(self):
        self.assert_permissions(
            self.system_admin,
            self.project_a1,
            view=True,
            work=True,
            administer=True,
            financial=True,
        )

    def test_client_admin_has_all_permissions_in_environment(self):
        self.assert_permissions(
            self.client_admin,
            self.project_a1,
            view=True,
            work=True,
            administer=True,
            financial=True,
        )

    def test_client_admin_has_no_permission_outside_environment(self):
        self.assert_permissions(
            self.client_admin,
            self.project_b1,
            view=False,
            work=False,
            administer=False,
            financial=False,
        )

    def test_responsible_project_manager_has_all_permissions(self):
        self.assert_permissions(
            self.responsible_project_manager,
            self.project_a1,
            view=True,
            work=True,
            administer=True,
            financial=True,
        )

    def test_delegate_project_manager_has_same_permissions(self):
        self.assert_permissions(
            self.delegate_project_manager,
            self.project_a1,
            view=True,
            work=True,
            administer=True,
            financial=True,
        )

    def test_project_manager_has_read_only_transverse_access(self):
        self.assert_permissions(
            self.responsible_project_manager,
            self.project_a2,
            view=True,
            work=False,
            administer=False,
            financial=False,
        )

    def test_standard_member_can_view_and_work(self):
        self.assert_permissions(
            self.standard_user,
            self.project_a1,
            view=True,
            work=True,
            administer=False,
            financial=False,
        )

    def test_read_only_member_can_only_view(self):
        self.assert_permissions(
            self.read_only_user,
            self.project_a1,
            view=True,
            work=False,
            administer=False,
            financial=False,
        )

    def test_outsider_has_no_permission(self):
        self.assert_permissions(
            self.outsider,
            self.project_a1,
            view=False,
            work=False,
            administer=False,
            financial=False,
        )

    def test_inactive_system_admin_has_no_permission(self):
        self.assert_permissions(
            self.inactive_system_admin,
            self.project_a1,
            view=False,
            work=False,
            administer=False,
            financial=False,
        )