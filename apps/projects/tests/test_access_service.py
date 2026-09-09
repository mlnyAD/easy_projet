

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import Project, ProjectMembership
from apps.projects.services.access import ProjectAccessService
from apps.users.models import User


class ProjectAccessServiceTests(TestCase):
    """
    Tests des règles de périmètre projet.

    Ces tests utilisent le modèle de droits Niveau 2 :
    - User.is_system_admin pour l'administration système ;
    - ClientEnvironmentMembership pour l'administration client ;
    - ProjectMembership pour l'accès direct à un projet ;
    - un Chef de projet dispose également d'une visibilité
      transverse en lecture sur les autres projets de la société
      d'un projet qu'il dirige.

    La visibilité transverse d'un Chef de projet est déterminée
    par la société du projet dirigé, et non par la société
    employeur du User.
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
        # Catalogue de statut projet
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
        # Catalogue des rôles projet
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
        # Catalogue des niveaux d'accès projet
        # --------------------------------------------------------------

        cls.project_access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès projet",
        )

        cls.project_access_level = CatalogValue.objects.create(
            catalog_type=cls.project_access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
            is_default=True,
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

        cls.project_b2 = Project.objects.create(
            company=cls.company_b,
            reference="B-002",
            name="Projet B2",
            status=cls.project_status,
        )

        cls.project_b_inactive = Project.objects.create(
            company=cls.company_b,
            reference="B-003",
            name="Projet B inactif",
            status=cls.project_status,
            is_active=False,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="system-admin@example.com",
            first_name="Admin",
            last_name="Système",
            is_system_admin=True,
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="client-admin@example.com",
            first_name="Admin",
            last_name="Client",
        )

        cls.project_user = User.objects.create(
            company=cls.company_a,
            email="project-user@example.com",
            first_name="Utilisateur",
            last_name="Projet",
        )

        cls.itinerant_user = User.objects.create(
            company=cls.company_a,
            email="itinerant@example.com",
            first_name="Utilisateur",
            last_name="Itinérant",
        )

        cls.project_manager_a = User.objects.create(
            company=cls.company_a,
            email="project-manager-a@example.com",
            first_name="Chef",
            last_name="Projet A",
        )

        cls.itinerant_project_manager = User.objects.create(
            company=cls.company_a,
            email="itinerant-project-manager@example.com",
            first_name="Chef",
            last_name="Projet itinérant",
        )

        cls.inactive_user = User.objects.create(
            company=cls.company_a,
            email="inactive@example.com",
            first_name="Utilisateur",
            last_name="Inactif",
            is_active=False,
        )

        cls.inactive_client_admin = User.objects.create(
            company=cls.company_a,
            email="inactive-client-admin@example.com",
            first_name="Admin",
            last_name="Client inactif",
        )

        cls.inactive_project_user = User.objects.create(
            company=cls.company_a,
            email="inactive-project-user@example.com",
            first_name="Utilisateur",
            last_name="Membership inactif",
        )

        # --------------------------------------------------------------
        # Administration environnement client
        # --------------------------------------------------------------

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.client_admin,
            is_client_admin=True,
            is_active=True,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.itinerant_user,
            is_client_admin=True,
            is_active=True,
        )

        ClientEnvironmentMembership.objects.create(
            client_environment=cls.environment_a,
            user=cls.inactive_client_admin,
            is_client_admin=True,
            is_active=False,
        )

        # --------------------------------------------------------------
        # Participations projet
        # --------------------------------------------------------------

        ProjectMembership.objects.create(
            project=cls.project_b1,
            user=cls.project_user,
            role=cls.project_user_role,
            access_level=cls.project_access_level,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_b1,
            user=cls.itinerant_user,
            role=cls.project_user_role,
            access_level=cls.project_access_level,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_a1,
            user=cls.project_manager_a,
            role=cls.project_manager_role,
            access_level=cls.project_access_level,
            is_project_manager_responsible=True,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_b1,
            user=cls.itinerant_project_manager,
            role=cls.project_manager_role,
            access_level=cls.project_access_level,
            is_project_manager_responsible=True,
            is_active=True,
        )

        ProjectMembership.objects.create(
            project=cls.project_b1,
            user=cls.inactive_project_user,
            role=cls.project_user_role,
            access_level=cls.project_access_level,
            is_active=False,
        )

    def accessible_project_ids(self, user):
        return set(
            ProjectAccessService
            .get_accessible_projects(user)
            .values_list("pk", flat=True)
        )

    def test_inactive_user_has_no_access(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.inactive_user
            ),
            set(),
        )

    def test_system_admin_has_access_to_all_active_projects(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.system_admin
            ),
            {
                self.project_a1.pk,
                self.project_a2.pk,
                self.project_b1.pk,
                self.project_b2.pk,
            },
        )

    def test_client_admin_has_access_to_environment_projects(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.client_admin
            ),
            {
                self.project_a1.pk,
                self.project_a2.pk,
            },
        )

    def test_project_membership_grants_project_access(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.project_user
            ),
            {
                self.project_b1.pk,
            },
        )

    def test_client_admin_and_project_membership_are_combined(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.itinerant_user
            ),
            {
                self.project_a1.pk,
                self.project_a2.pk,
                self.project_b1.pk,
            },
        )

    def test_inactive_client_environment_membership_grants_no_access(
        self,
    ):
        self.assertEqual(
            self.accessible_project_ids(
                self.inactive_client_admin
            ),
            set(),
        )

    def test_inactive_project_membership_grants_no_access(self):
        self.assertEqual(
            self.accessible_project_ids(
                self.inactive_project_user
            ),
            set(),
        )

    def test_inactive_project_is_never_accessible(self):
        self.assertNotIn(
            self.project_b_inactive.pk,
            self.accessible_project_ids(
                self.system_admin
            ),
        )

    def test_can_access_project_returns_true_for_accessible_project(
        self,
    ):
        self.assertTrue(
            ProjectAccessService.can_access_project(
                self.project_user,
                self.project_b1,
            )
        )

    def test_can_access_project_returns_false_for_foreign_project(
        self,
    ):
        self.assertFalse(
            ProjectAccessService.can_access_project(
                self.project_user,
                self.project_a1,
            )
        )

    def test_project_manager_sees_other_projects_of_managed_company(
        self,
    ):
        """
        Un Chef de projet voit son projet ainsi que les autres
        projets actifs de la société de ce projet.
        """

        self.assertEqual(
            self.accessible_project_ids(
                self.project_manager_a
            ),
            {
                self.project_a1.pk,
                self.project_a2.pk,
            },
        )

    def test_project_manager_does_not_see_projects_of_other_company(
        self,
    ):
        """
        La visibilité transverse du Chef de projet ne franchit
        pas la frontière de la société du projet dirigé.
        """

        self.assertNotIn(
            self.project_b1.pk,
            self.accessible_project_ids(
                self.project_manager_a
            ),
        )

        self.assertNotIn(
            self.project_b2.pk,
            self.accessible_project_ids(
                self.project_manager_a
            ),
        )

    def test_itinerant_project_manager_visibility_uses_project_company(
        self,
    ):
        """
        Le périmètre transverse du Chef de projet dépend de la
        société du projet dirigé et non de son employeur.

        L'utilisateur est employé par la société A mais Chef de
        projet du projet B1.

        Il voit donc :
        - B1 par son ProjectMembership ;
        - B2 par visibilité transverse de Chef de projet.

        Son emploi par la société A ne lui donne aucun accès
        automatique à A1 ou A2.
        """

        self.assertEqual(
            self.accessible_project_ids(
                self.itinerant_project_manager
            ),
            {
                self.project_b1.pk,
                self.project_b2.pk,
            },
        )