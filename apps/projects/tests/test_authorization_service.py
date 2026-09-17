

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

    Création d'un projet :
    - administrateur système :
      toute société active disposant d'un environnement client actif ;
    - administrateur client :
      sociétés des environnements clients actifs qu'il administre ;
    - chef de projet :
      sociétés des projets actifs qu'il dirige ;
    - membre STANDARD ou READ_ONLY :
      aucun droit de création ;
    - utilisateur inactif :
      aucun droit de création.

    Le périmètre de création d'un chef de projet dépend des sociétés
    des projets qu'il dirige et non de sa société employeur.
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

        cls.company_c = Company.objects.create(
            name="Société cliente C",
        )

        cls.company_without_environment = Company.objects.create(
            name="Société sans environnement",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        cls.environment_c = ClientEnvironment.objects.create(
            company=cls.company_c,
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

        cls.project_c1 = Project.objects.create(
            company=cls.company_c,
            reference="C-001",
            name="Projet C1",
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

        cls.itinerant_project_manager = User.objects.create(
            company=cls.company_b,
            email="itinerant-pm-auth@example.com",
            first_name="Chef",
            last_name="Projet itinérant",
        )

        cls.client_admin_and_project_manager = User.objects.create(
            company=cls.company_a,
            email="client-admin-pm-auth@example.com",
            first_name="Admin et chef",
            last_name="Projet",
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

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin_and_project_manager,
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

        ProjectMembership.objects.create(
            project=cls.project_c1,
            user=cls.itinerant_project_manager,
            role=cls.project_manager_role,
            access_level=cls.standard_access,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_b1,
            user=cls.client_admin_and_project_manager,
            role=cls.project_manager_role,
            access_level=cls.standard_access,
            is_active=True,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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

    def assert_administrable_projects(
        self,
        user,
        *projects,
    ):
        queryset = (
            ProjectAuthorizationService
            .get_administrable_projects(user)
        )

        self.assertQuerySetEqual(
            queryset,
            projects,
            ordered=False,
        )
        
    def assert_financially_accessible_projects(
        self,
        user,
        *projects,
    ):
        queryset = (
            ProjectAuthorizationService
            .get_financially_accessible_projects(user)
        )

        self.assertQuerySetEqual(
            queryset,
            projects,
            ordered=False,
        )
        
    def assert_workable_projects(
        self,
        user,
        *projects,
    ):
        queryset = (
            ProjectAuthorizationService
            .get_workable_projects(user)
        )

        self.assertQuerySetEqual(
            queryset,
            projects,
            ordered=False,
        )

    def assert_project_creation_companies(
        self,
        user,
        *companies,
    ):
        queryset = (
            ProjectAuthorizationService
            .get_project_creation_companies(user)
        )

        self.assertQuerySetEqual(
            queryset,
            companies,
            ordered=False,
        )

    # ------------------------------------------------------------------
    # Autorisations unitaires
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Projets administrables
    # ------------------------------------------------------------------

    def test_system_admin_can_administer_all_active_projects(self):
        self.assert_administrable_projects(
            self.system_admin,
            self.project_a1,
            self.project_a2,
            self.project_b1,
            self.project_c1,
        )

    def test_client_admin_can_administer_environment_projects(self):
        self.assert_administrable_projects(
            self.client_admin,
            self.project_a1,
            self.project_a2,
        )

    def test_responsible_project_manager_administers_only_own_project(
        self,
    ):
        self.assert_administrable_projects(
            self.responsible_project_manager,
            self.project_a1,
        )

    def test_delegate_project_manager_administers_only_own_project(
        self,
    ):
        self.assert_administrable_projects(
            self.delegate_project_manager,
            self.project_a1,
        )

    def test_standard_member_has_no_administrable_project(self):
        self.assert_administrable_projects(
            self.standard_user,
        )

    def test_read_only_member_has_no_administrable_project(self):
        self.assert_administrable_projects(
            self.read_only_user,
        )

    def test_inactive_system_admin_has_no_administrable_project(self):
        self.assert_administrable_projects(
            self.inactive_system_admin,
        )

    # ------------------------------------------------------------------
    # Sociétés autorisées pour la création d'un projet
    # ------------------------------------------------------------------

    def test_system_admin_can_create_project_for_all_active_environments(
        self,
    ):
        self.assert_project_creation_companies(
            self.system_admin,
            self.company_a,
            self.company_b,
            self.company_c,
        )

    def test_company_without_environment_is_not_available_for_creation(
        self,
    ):
        self.assertNotIn(
            self.company_without_environment,
            ProjectAuthorizationService
            .get_project_creation_companies(self.system_admin),
        )

    def test_client_admin_can_create_project_for_administered_environment(
        self,
    ):
        self.assert_project_creation_companies(
            self.client_admin,
            self.company_a,
        )

    def test_responsible_project_manager_can_create_for_managed_company(
        self,
    ):
        self.assert_project_creation_companies(
            self.responsible_project_manager,
            self.company_a,
        )

    def test_delegate_project_manager_can_create_for_managed_company(
        self,
    ):
        self.assert_project_creation_companies(
            self.delegate_project_manager,
            self.company_a,
        )

    def test_itinerant_project_manager_uses_managed_project_company(
        self,
    ):
        self.assert_project_creation_companies(
            self.itinerant_project_manager,
            self.company_c,
        )

    def test_client_admin_and_project_manager_accumulate_creation_scope(
        self,
    ):
        self.assert_project_creation_companies(
            self.client_admin_and_project_manager,
            self.company_a,
            self.company_b,
        )

    def test_users_without_creation_role_have_no_creation_company(
        self,
    ):
        for user in (
            self.standard_user,
            self.read_only_user,
            self.outsider,
            self.inactive_system_admin,
        ):
            with self.subTest(user=user.email):
                self.assert_project_creation_companies(user)
                
        # ------------------------------------------------------------------
    # Projets financièrement accessibles
    # ------------------------------------------------------------------

    def test_system_admin_can_access_financial_data_for_all_projects(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.system_admin,
            self.project_a1,
            self.project_a2,
            self.project_b1,
            self.project_c1,
        )

    def test_client_admin_can_access_environment_financial_data(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.client_admin,
            self.project_a1,
            self.project_a2,
        )

    def test_responsible_project_manager_can_access_own_financial_data(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.responsible_project_manager,
            self.project_a1,
        )

    def test_delegate_project_manager_can_access_own_financial_data(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.delegate_project_manager,
            self.project_a1,
        )

    def test_itinerant_project_manager_uses_managed_project_scope(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.itinerant_project_manager,
            self.project_c1,
        )

    def test_client_admin_and_project_manager_accumulate_financial_scope(
        self,
    ):
        self.assert_financially_accessible_projects(
            self.client_admin_and_project_manager,
            self.project_a1,
            self.project_a2,
            self.project_b1,
        )

    def test_users_without_financial_access_have_no_project_scope(
        self,
    ):
        for user in (
            self.standard_user,
            self.read_only_user,
            self.outsider,
            self.inactive_system_admin,
        ):
            with self.subTest(user=user.email):
                self.assert_financially_accessible_projects(
                    user,
                )
    
    # ------------------------------------------------------------------
    # Projets accessibles pour le travail opérationnel
    # ------------------------------------------------------------------

    def test_system_admin_can_work_on_all_projects(self):
        self.assert_workable_projects(
            self.system_admin,
            self.project_a1,
            self.project_a2,
            self.project_b1,
            self.project_c1,
        )

    def test_client_admin_can_work_on_environment_projects(self):
        self.assert_workable_projects(
            self.client_admin,
            self.project_a1,
            self.project_a2,
        )

    def test_responsible_project_manager_can_work_on_own_project_only(
        self,
    ):
        self.assert_workable_projects(
            self.responsible_project_manager,
            self.project_a1,
        )

    def test_delegate_project_manager_can_work_on_own_project_only(
        self,
    ):
        self.assert_workable_projects(
            self.delegate_project_manager,
            self.project_a1,
        )

    def test_standard_member_can_work_on_own_project_only(self):
        self.assert_workable_projects(
            self.standard_user,
            self.project_a1,
        )

    def test_itinerant_project_manager_can_work_on_managed_project(
        self,
    ):
        self.assert_workable_projects(
            self.itinerant_project_manager,
            self.project_c1,
        )

    def test_client_admin_and_project_manager_accumulate_work_scope(
        self,
    ):
        self.assert_workable_projects(
            self.client_admin_and_project_manager,
            self.project_a1,
            self.project_a2,
            self.project_b1,
        )

    def test_users_without_work_right_have_no_project_scope(self):
        for user in (
            self.read_only_user,
            self.outsider,
            self.inactive_system_admin,
        ):
            with self.subTest(user=user.email):
                self.assert_workable_projects(user)