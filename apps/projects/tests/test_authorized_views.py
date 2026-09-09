

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class ProjectAuthorizedViewTests(TestCase):
    """
    Tests d'autorisation des vues d'administration Projet.

    Les vues de modification du projet et de sa photo utilisent
    le même périmètre d'administration.

    Sont autorisés :
    - l'administrateur système ;
    - l'administrateur client de l'environnement ;
    - le Chef de projet du projet, titulaire ou délégué.

    Ne sont pas autorisés :
    - le Chef de projet bénéficiant uniquement d'une visibilité
      transverse ;
    - le membre STANDARD ;
    - le membre READ_ONLY ;
    - l'utilisateur hors périmètre.

    Une ressource non administrable est absente du queryset
    de la vue et produit donc une réponse HTTP 404.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés et environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société cliente A - vues",
        )

        cls.company_b = Company.objects.create(
            name="Société cliente B - vues",
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

        cls.project_access_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau d'accès projet",
        )

        cls.standard_access = CatalogValue.objects.create(
            catalog_type=cls.project_access_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
            is_default=True,
        )

        cls.read_only_access = CatalogValue.objects.create(
            catalog_type=cls.project_access_type,
            code="READ_ONLY",
            label="Lecture seule",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project_a1 = Project.objects.create(
            company=cls.company_a,
            reference="AUTH-A-001",
            name="Projet A1 autorisations vues",
            status=cls.project_status,
        )

        cls.project_a2 = Project.objects.create(
            company=cls.company_a,
            reference="AUTH-A-002",
            name="Projet A2 autorisations vues",
            status=cls.project_status,
        )

        cls.project_b1 = Project.objects.create(
            company=cls.company_b,
            reference="AUTH-B-001",
            name="Projet B1 autorisations vues",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.system_admin = User.objects.create(
            company=cls.company_a,
            email="system-admin-view@example.com",
            first_name="Admin",
            last_name="Système",
            is_system_admin=True,
        )

        cls.client_admin = User.objects.create(
            company=cls.company_a,
            email="client-admin-view@example.com",
            first_name="Admin",
            last_name="Client",
        )

        cls.responsible_project_manager = User.objects.create(
            company=cls.company_a,
            email="responsible-pm-view@example.com",
            first_name="Chef",
            last_name="Projet titulaire",
        )

        cls.delegate_project_manager = User.objects.create(
            company=cls.company_a,
            email="delegate-pm-view@example.com",
            first_name="Chef",
            last_name="Projet délégué",
        )

        cls.standard_user = User.objects.create(
            company=cls.company_a,
            email="standard-view@example.com",
            first_name="Utilisateur",
            last_name="Standard",
        )

        cls.read_only_user = User.objects.create(
            company=cls.company_a,
            email="readonly-view@example.com",
            first_name="Utilisateur",
            last_name="Lecture seule",
        )

        cls.outsider = User.objects.create(
            company=cls.company_b,
            email="outsider-view@example.com",
            first_name="Utilisateur",
            last_name="Hors périmètre",
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
        # Participations au projet A1
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_update_url(self, project):
        return reverse(
            "projects:update",
            kwargs={
                "pk": project.pk,
            },
        )

    def get_photo_url(self, project):
        return reverse(
            "projects:photo",
            kwargs={
                "pk": project.pk,
            },
        )

    def assert_view_status(
        self,
        *,
        user,
        project,
        expected_status,
    ):
        self.client.force_login(user)

        update_response = self.client.get(
            self.get_update_url(project)
        )

        self.assertEqual(
            update_response.status_code,
            expected_status,
        )

        photo_response = self.client.get(
            self.get_photo_url(project)
        )

        self.assertEqual(
            photo_response.status_code,
            expected_status,
        )

        self.client.logout()

    # ------------------------------------------------------------------
    # Utilisateurs autorisés
    # ------------------------------------------------------------------

    def test_system_admin_can_access_administration_views(self):
        self.assert_view_status(
            user=self.system_admin,
            project=self.project_a1,
            expected_status=200,
        )

    def test_client_admin_can_access_environment_project_views(self):
        self.assert_view_status(
            user=self.client_admin,
            project=self.project_a1,
            expected_status=200,
        )

    def test_responsible_project_manager_can_access_own_project_views(
        self,
    ):
        self.assert_view_status(
            user=self.responsible_project_manager,
            project=self.project_a1,
            expected_status=200,
        )

    def test_delegate_project_manager_can_access_own_project_views(
        self,
    ):
        self.assert_view_status(
            user=self.delegate_project_manager,
            project=self.project_a1,
            expected_status=200,
        )

    # ------------------------------------------------------------------
    # Utilisateurs non autorisés
    # ------------------------------------------------------------------

    def test_client_admin_cannot_access_other_environment_views(self):
        self.assert_view_status(
            user=self.client_admin,
            project=self.project_b1,
            expected_status=404,
        )

    def test_project_manager_cannot_administer_transverse_project(self):
        self.assert_view_status(
            user=self.responsible_project_manager,
            project=self.project_a2,
            expected_status=404,
        )

    def test_standard_member_cannot_access_administration_views(self):
        self.assert_view_status(
            user=self.standard_user,
            project=self.project_a1,
            expected_status=404,
        )

    def test_read_only_member_cannot_access_administration_views(self):
        self.assert_view_status(
            user=self.read_only_user,
            project=self.project_a1,
            expected_status=404,
        )

    def test_outsider_cannot_access_administration_views(self):
        self.assert_view_status(
            user=self.outsider,
            project=self.project_a1,
            expected_status=404,
        )