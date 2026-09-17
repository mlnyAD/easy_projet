

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

    def assert_project_update_read_only(
        self,
        *,
        user,
        project,
    ):
        """
        Vérifie l'ouverture en lecture seule d'un projet visible.

        La photo reste une opération d'administration et demeure
        inaccessible à l'utilisateur non administrateur.
        """

        self.client.force_login(user)

        update_response = self.client.get(
            self.get_update_url(project)
        )

        self.assertEqual(
            update_response.status_code,
            200,
        )

        self.assertTrue(
            update_response.context[
                "form_view"
            ].is_readonly,
        )

        update_post_response = self.client.post(
            self.get_update_url(project),
            data={},
        )

        self.assertEqual(
            update_post_response.status_code,
            403,
        )

        photo_response = self.client.get(
            self.get_photo_url(project)
        )

        self.assertEqual(
            photo_response.status_code,
            404,
        )

        self.client.logout()

    def get_create_url(self):
        return reverse("projects:create")

    def get_creation_company_queryset(self, user):
        self.client.force_login(user)

        response = self.client.get(
            self.get_create_url()
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        queryset = (
            response.context["form"]
            .fields["company"]
            .queryset
        )

        self.client.logout()

        return queryset

    def build_creation_data(
        self,
        *,
        company,
        reference,
    ):
        return {
            "reference": reference,
            "name": f"Projet {reference}",
            "description": "",
            "company": str(company.pk),
            "status": str(self.project_status.pk),
            "is_active": "on",
            "owner_company": "",
            "designer_company": "",
            "project_type": "",
            "contract_reference": "",
            "comments": "",
            "address_1": "",
            "address_2": "",
            "address_3": "",
            "postal_code": "",
            "city": "",
            "country": "",
            "planned_workload_hours": "0",
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "initial_receipt_date": "",
            "receipt_date": "",
            "initial_delivery_date": "",
            "delivery_date": "",
            "amount_quote_ht": "0.00",
            "amount_quote_ttc": "0.00",
            "amount_order_ht": "0.00",
            "amount_order_ttc": "0.00",
            "currency": "EUR",
            "budget_comments": "",

            "memberships-TOTAL_FORMS": "0",
            "memberships-INITIAL_FORMS": "0",
            "memberships-MIN_NUM_FORMS": "0",
            "memberships-MAX_NUM_FORMS": "1000",

            "external_participants-TOTAL_FORMS": "0",
            "external_participants-INITIAL_FORMS": "0",
            "external_participants-MIN_NUM_FORMS": "0",
            "external_participants-MAX_NUM_FORMS": "1000",
        }
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

    def test_project_manager_opens_transverse_project_read_only(self):
        self.assert_project_update_read_only(
            user=self.responsible_project_manager,
            project=self.project_a2,
        )

    def test_standard_member_opens_project_read_only(self):
        self.assert_project_update_read_only(
            user=self.standard_user,
            project=self.project_a1,
        )

    def test_read_only_member_opens_project_read_only(self):
        self.assert_project_update_read_only(
            user=self.read_only_user,
            project=self.project_a1,
        )

    def test_outsider_cannot_access_administration_views(self):
        self.assert_view_status(
            user=self.outsider,
            project=self.project_a1,
            expected_status=404,
        )
        
    # ------------------------------------------------------------------
    # Création d'un projet
    # ------------------------------------------------------------------

    def test_system_admin_sees_all_creation_companies(self):
        queryset = self.get_creation_company_queryset(
            self.system_admin
        )

        self.assertQuerySetEqual(
            queryset,
            (
                self.company_a,
                self.company_b,
            ),
            ordered=False,
        )

    def test_client_admin_sees_administered_company_only(self):
        queryset = self.get_creation_company_queryset(
            self.client_admin
        )

        self.assertQuerySetEqual(
            queryset,
            (
                self.company_a,
            ),
            ordered=False,
        )

    def test_project_manager_sees_managed_project_company_only(self):
        queryset = self.get_creation_company_queryset(
            self.responsible_project_manager
        )

        self.assertQuerySetEqual(
            queryset,
            (
                self.company_a,
            ),
            ordered=False,
        )

    def test_user_without_creation_scope_cannot_access_create_view(
            self,
        ):
            self.client.force_login(
                self.standard_user
            )

            response = self.client.get(
                self.get_create_url()
            )

            self.assertEqual(
                response.status_code,
                403,
            )
        
    def test_client_admin_can_create_project_for_administered_company(
        self,
    ):
        self.client.force_login(
            self.client_admin
        )

        data = self.build_creation_data(
            company=self.company_a,
            reference="CREATE-A-001",
        )

        response = self.client.post(
            self.get_create_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Project.objects.filter(
                reference="CREATE-A-001",
                company=self.company_a,
            ).exists()
        )

    def test_client_admin_cannot_create_project_for_other_company(
        self,
    ):
        self.client.force_login(
            self.client_admin
        )

        data = self.build_creation_data(
            company=self.company_b,
            reference="CREATE-B-FORBIDDEN",
        )

        response = self.client.post(
            self.get_create_url(),
            data,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "company",
            response.context["form"].errors,
        )

        self.assertFalse(
            Project.objects.filter(
                reference="CREATE-B-FORBIDDEN",
            ).exists()
        )
        
        # ------------------------------------------------------------------
    # Action de création dans la liste
    # ------------------------------------------------------------------

    def test_creation_action_is_visible_for_authorized_user(self):
        self.client.force_login(
            self.system_admin
        )

        response = self.client.get(
            reverse("projects:list")
        )

        self.assertTrue(
            response.context["can_create_project"]
        )
        self.assertContains(
            response,
            "Nouveau projet",
        )

    def test_creation_action_is_hidden_for_unauthorized_user(self):
        self.client.force_login(
            self.standard_user
        )

        response = self.client.get(
            reverse("projects:list")
        )

        self.assertFalse(
            response.context["can_create_project"]
        )
        self.assertNotContains(
            response,
            "Nouveau projet",
        )

    def test_standard_member_sees_project_open_action(self):
        self.client.force_login(
            self.standard_user
        )

        response = self.client.get(
            reverse("projects:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.get_update_url(
                self.project_a1
            ),
        )
