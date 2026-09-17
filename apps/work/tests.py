

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.users.models import User

from apps.work.models import WorkPackage


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class WorkPackageAccessTests(TestCase):
    """
    Tests de cloisonnement des lots de travaux par projet accessible.

    L'utilisateur est affecté uniquement au projet A.
    Le projet B appartient à un autre environnement client.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Work",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Work",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------



        cls.access_level_type = CatalogType.objects.create(
            code="USER_LEVEL_ACCESS",
            label="Niveau accès test Work",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateur connecté
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company_a,
            email="work-user@example.com",
            first_name="Jean",
            last_name="Work",
        )
        
        cls.project_manager = User.objects.create(
            company=cls.company_a,
            email="work-project-manager@example.com",
            first_name="Marie",
            last_name="Chef de projet",
        )
        # --------------------------------------------------------------
        # Rôle projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle sur projet",
        )

        cls.project_role = CatalogValue.objects.create(
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
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_WORK_PROJECT_STATUS",
            label="Statut projet test Work",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut lot de travaux
        #
        # Celui-ci utilise volontairement le vrai code attendu
        # par WorkPackageForm.
        # --------------------------------------------------------------

        cls.work_status_type = CatalogType.objects.create(
            code="WORK_PACKAGE_STATUS",
            label="Statut lot de travaux",
        )

        cls.work_status = CatalogValue.objects.create(
            catalog_type=cls.work_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
            is_default=True,
        )

        # --------------------------------------------------------------
        # Projets A et B
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-WORK-A",
            name="Projet Work A",
            status=cls.project_status,
        )

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-WORK-B",
            name="Projet Work B",
            status=cls.project_status,
        )

        # L'utilisateur est affecté uniquement au projet A.

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.user,
            role=cls.project_role,
            access_level=cls.access_level,
        )

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.project_manager,
            role=cls.project_manager_role,
            access_level=cls.access_level,
            is_active=True,
        )
        # --------------------------------------------------------------
        # Lots de travaux
        # --------------------------------------------------------------

        cls.work_package_a = WorkPackage.objects.create(
            project=cls.project_a,
            status=cls.work_status,
            name="Lot accessible A",
        )

        cls.work_package_b = WorkPackage.objects.create(
            project=cls.project_b,
            status=cls.work_status,
            name="Lot inaccessible B",
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def build_post_data(
        self,
        *,
        project,
        work_package=None,
        name="Lot formulaire",
    ):
        return {
            "project": str(project.pk),
            "code": (
                work_package.code
                if work_package is not None
                else ""
            ),
            "name": name,
            "description": "",
            "status": str(self.work_status.pk),
            "manager": "",
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": "0",
            "is_active": "on",
        }

    # ------------------------------------------------------------------
    # Liste globale
    # ------------------------------------------------------------------

    def test_global_list_only_contains_accessible_work_packages(
        self,
    ):
        response = self.client.get(
            reverse("work:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.work_package_a.name,
        )

        self.assertNotContains(
            response,
            self.work_package_b.name,
        )

    # ------------------------------------------------------------------
    # Liste par projet
    # ------------------------------------------------------------------

    def test_accessible_project_list_returns_200(self):
        response = self.client.get(
            reverse(
                "work:list-by-project",
                kwargs={
                    "project_pk": self.project_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_inaccessible_project_list_returns_404(self):
        response = self.client.get(
            reverse(
                "work:list-by-project",
                kwargs={
                    "project_pk": self.project_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_form_only_contains_accessible_projects(self):
        
        self.client.force_login(
            self.project_manager
        )
                
        response = self.client.get(
            reverse("work:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        form = response.context["form"]

        project_ids = set(
            form.fields["project"]
            .queryset
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.project_a.pk,
            project_ids,
        )

        self.assertNotIn(
            self.project_b.pk,
            project_ids,
        )

    def test_create_with_accessible_project_succeeds(self):
        
        self.client.force_login(
            self.project_manager
        )
                        
        response = self.client.post(
            reverse("work:create"),
            data=self.build_post_data(
                project=self.project_a,
                name="Nouveau lot A",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            WorkPackage.objects.filter(
                project=self.project_a,
                name="Nouveau lot A",
            ).exists()
        )

    def test_create_with_inaccessible_project_is_rejected(self):
        self.client.force_login(
            self.project_manager
        )
                        
        initial_count = (
            WorkPackage.objects
            .filter(
                project=self.project_b,
            )
            .count()
        )

        response = self.client.post(
            reverse("work:create"),
            data=self.build_post_data(
                project=self.project_b,
                name="Tentative lot B",
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            WorkPackage.objects
            .filter(
                project=self.project_b,
            )
            .count(),
            initial_count,
        )

    # ------------------------------------------------------------------
    # Modification
    # ------------------------------------------------------------------

    def test_accessible_work_package_update_returns_200(self):
        self.client.force_login(
            self.project_manager
        )
                
        response = self.client.get(
            reverse(
                "work:update",
                kwargs={
                    "pk": self.work_package_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertFalse(
            response.context[
                "form_view"
            ].is_readonly,
        )

    def test_inaccessible_work_package_update_returns_404(self):
        self.client.force_login(
            self.project_manager
        )
                
        response = self.client.get(
            reverse(
                "work:update",
                kwargs={
                    "pk": self.work_package_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_cannot_move_work_package_to_inaccessible_project(
        self,
    ):
        self.client.force_login(
            self.project_manager
        )
                
        response = self.client.post(
            reverse(
                "work:update",
                kwargs={
                    "pk": self.work_package_a.pk,
                },
            ),
            data=self.build_post_data(
                project=self.project_b,
                work_package=self.work_package_a,
                name=self.work_package_a.name,
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.work_package_a.refresh_from_db()

        self.assertEqual(
            self.work_package_a.project_id,
            self.project_a.pk,
        )

    def test_standard_user_cannot_access_create_view(self):
        response = self.client.get(
            reverse("work:create")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_standard_user_opens_visible_work_package_read_only(self):
        response = self.client.get(
            reverse(
                "work:update",
                kwargs={
                    "pk": self.work_package_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTrue(
            response.context[
                "form_view"
            ].is_readonly,
        )

        post_response = self.client.post(
            reverse(
                "work:update",
                kwargs={
                    "pk": self.work_package_a.pk,
                },
            ),
            data=self.build_post_data(
                project=self.project_a,
                work_package=self.work_package_a,
                name="Modification interdite",
            ),
        )

        self.assertEqual(
            post_response.status_code,
            403,
        )

        self.work_package_a.refresh_from_db()

        self.assertEqual(
            self.work_package_a.name,
            "Lot accessible A",
        )
    
        # ------------------------------------------------------------------
    # Interface lecture seule / lecture-écriture
    # ------------------------------------------------------------------

    def test_standard_user_sees_work_package_in_read_only_mode(self):
        response = self.client.get(
            reverse(
                "work:list-by-project",
                kwargs={
                    "project_pk": self.project_a.pk,
                },
            )
        )

        task_list_url = reverse(
            "tasks:list-by-work-package",
            kwargs={
                "work_package_pk": self.work_package_a.pk,
            },
        )

        update_url = reverse(
            "work:update",
            kwargs={
                "pk": self.work_package_a.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNone(
            response.context["page_action_url"]
        )

        self.assertContains(
            response,
            task_list_url,
        )

        self.assertContains(
            response,
            update_url,
        )

        self.assertNotContains(
            response,
            "Nouveau lot de travaux",
        )

    def test_project_manager_sees_work_package_in_edit_mode(self):
        self.client.force_login(
            self.project_manager
        )

        response = self.client.get(
            reverse(
                "work:list-by-project",
                kwargs={
                    "project_pk": self.project_a.pk,
                },
            )
        )

        task_list_url = reverse(
            "tasks:list-by-work-package",
            kwargs={
                "work_package_pk": self.work_package_a.pk,
            },
        )

        update_url = reverse(
            "work:update",
            kwargs={
                "pk": self.work_package_a.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIsNotNone(
            response.context["page_action_url"]
        )

        self.assertContains(
            response,
            "Nouveau lot de travaux",
        )

        self.assertContains(
            response,
            task_list_url,
        )

        self.assertContains(
            response,
            update_url,
        )
