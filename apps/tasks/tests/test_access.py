

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
from apps.tasks.models import Task
from apps.users.models import User
from apps.work.models import WorkPackage


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class TaskAccessTests(TestCase):
    """
    Tests de cloisonnement Niveau 1 des tâches.

    L'utilisateur connecté est affecté uniquement au projet A.

    Le projet B appartient à un autre environnement client
    et ne doit jamais être visible ou utilisable depuis les
    vues et formulaires de tâches.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Tasks",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Tasks",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_TASK_ACCESS_GLOBAL_ROLE",
            label="Rôle global test accès tâches",
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_TASK_ACCESS_LEVEL",
            label="Niveau accès test tâches",
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
            email="task-access@example.com",
            first_name="Jean",
            last_name="Accès",
            global_role=cls.global_role,
            access_level=cls.access_level,
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

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_TASK_PROJECT_STATUS",
            label="Statut projet test accès tâches",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut lot de travaux
        # --------------------------------------------------------------

        cls.work_package_status_type = (
            CatalogType.objects.create(
                code="TEST_TASK_ACCESS_WP_STATUS",
                label="Statut lot test accès tâches",
            )
        )

        cls.work_package_status = (
            CatalogValue.objects.create(
                catalog_type=(
                    cls.work_package_status_type
                ),
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Statut tâche
        #
        # Le code TASK_STATUS est celui attendu par TaskForm.
        # --------------------------------------------------------------

        cls.task_status_type = CatalogType.objects.create(
            code="TASK_STATUS",
            label="Statut tâche",
        )

        cls.task_status = CatalogValue.objects.create(
            catalog_type=cls.task_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
            is_default=True,
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-TASK-A",
            name="Projet Tasks A",
            status=cls.project_status,
        )

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-TASK-B",
            name="Projet Tasks B",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Affectation
        #
        # L'utilisateur n'est membre que du projet A.
        # --------------------------------------------------------------

        ProjectMembership.objects.create(
            project=cls.project_a,
            user=cls.user,
            role=cls.project_role,
        )

        # --------------------------------------------------------------
        # Lots de travaux
        # --------------------------------------------------------------

        cls.work_package_a = WorkPackage.objects.create(
            project=cls.project_a,
            status=cls.work_package_status,
            name="Lot accessible A",
        )

        cls.work_package_b = WorkPackage.objects.create(
            project=cls.project_b,
            status=cls.work_package_status,
            name="Lot inaccessible B",
        )

        # --------------------------------------------------------------
        # Tâches
        # --------------------------------------------------------------

        cls.task_a = Task.objects.create(
            work_package=cls.work_package_a,
            status=cls.task_status,
            name="Tâche accessible A",
        )

        cls.task_b = Task.objects.create(
            work_package=cls.work_package_b,
            status=cls.task_status,
            name="Tâche inaccessible B",
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
        work_package,
        task=None,
        name="Tâche formulaire",
    ):
        """
        Construit un POST minimal valide pour TaskForm et ses
        deux collections inline.
        """

        return {
            "work_package": str(
                work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": (
                task.code
                if task is not None
                else ""
            ),
            "name": name,
            "description": "",
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": "0",
            "remaining_workload_hours": "0",
            "progress_percent": "0",
            "is_active": "on",

            # Personnel
            "assignments-TOTAL_FORMS": "0",
            "assignments-INITIAL_FORMS": "0",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            # Enchaînements
            "dependencies-TOTAL_FORMS": "0",
            "dependencies-INITIAL_FORMS": "0",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",
        }

    # ------------------------------------------------------------------
    # Liste globale
    # ------------------------------------------------------------------

    def test_global_list_only_contains_accessible_tasks(
        self,
    ):
        response = self.client.get(
            reverse("tasks:list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.task_a.name,
        )

        self.assertNotContains(
            response,
            self.task_b.name,
        )

    # ------------------------------------------------------------------
    # Liste par lot de travaux
    # ------------------------------------------------------------------

    def test_accessible_work_package_list_returns_200(
        self,
    ):
        response = self.client.get(
            reverse(
                "tasks:list-by-work-package",
                kwargs={
                    "work_package_pk": (
                        self.work_package_a.pk
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.task_a.name,
        )

    def test_inaccessible_work_package_list_returns_404(
        self,
    ):
        response = self.client.get(
            reverse(
                "tasks:list-by-work-package",
                kwargs={
                    "work_package_pk": (
                        self.work_package_b.pk
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Formulaire de création
    # ------------------------------------------------------------------

    def test_create_form_only_contains_accessible_work_packages(
        self,
    ):
        response = self.client.get(
            reverse("tasks:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        form = response.context["form"]

        work_package_ids = set(
            form.fields["work_package"]
            .queryset
            .values_list(
                "pk",
                flat=True,
            )
        )

        self.assertIn(
            self.work_package_a.pk,
            work_package_ids,
        )

        self.assertNotIn(
            self.work_package_b.pk,
            work_package_ids,
        )

    def test_create_does_not_preselect_inaccessible_work_package(
        self,
    ):
        response = self.client.get(
            reverse("tasks:create"),
            data={
                "work_package": (
                    str(self.work_package_b.pk)
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        form = response.context["form"]

        initial_work_package = (
            form.initial.get("work_package")
        )

        self.assertNotEqual(
            initial_work_package,
            self.work_package_b,
        )

    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_with_accessible_work_package_succeeds(
        self,
    ):
        response = self.client.post(
            reverse("tasks:create"),
            data=self.build_post_data(
                work_package=self.work_package_a,
                name="Nouvelle tâche A",
            ),
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Task.objects.filter(
                work_package=self.work_package_a,
                name="Nouvelle tâche A",
            ).exists()
        )

    def test_create_with_inaccessible_work_package_is_rejected(
        self,
    ):
        initial_count = (
            Task.objects
            .filter(
                work_package=self.work_package_b,
            )
            .count()
        )

        response = self.client.post(
            reverse("tasks:create"),
            data=self.build_post_data(
                work_package=self.work_package_b,
                name="Tentative tâche B",
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            Task.objects
            .filter(
                work_package=self.work_package_b,
            )
            .count(),
            initial_count,
        )

        self.assertFalse(
            Task.objects.filter(
                name="Tentative tâche B",
            ).exists()
        )

    # ------------------------------------------------------------------
    # Modification directe
    # ------------------------------------------------------------------

    def test_accessible_task_update_returns_200(
        self,
    ):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_inaccessible_task_update_returns_404(
        self,
    ):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_cannot_move_task_to_inaccessible_work_package(
        self,
    ):
        response = self.client.post(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task_a.pk,
                },
            ),
            data=self.build_post_data(
                work_package=self.work_package_b,
                task=self.task_a,
                name=self.task_a.name,
            ),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.task_a.refresh_from_db()

        self.assertEqual(
            self.task_a.work_package_id,
            self.work_package_a.pk,
        )

    # ------------------------------------------------------------------
    # Données exposées au JavaScript
    # ------------------------------------------------------------------

    def test_create_context_only_exposes_accessible_work_packages(
        self,
    ):
        response = self.client.get(
            reverse("tasks:create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        work_package_ids = {
            item["id"]
            for item
            in response.context[
                "task_work_packages_data"
            ]
        }

        self.assertIn(
            str(self.work_package_a.pk),
            work_package_ids,
        )

        self.assertNotIn(
            str(self.work_package_b.pk),
            work_package_ids,
        )
