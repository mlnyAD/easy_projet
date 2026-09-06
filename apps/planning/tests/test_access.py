

from datetime import date

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
from apps.tasks.models import (
    Task,
    TaskAssignment,
)
from apps.users.models import User
from apps.work.models import WorkPackage


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class PlanningAccessTests(TestCase):
    """
    Tests de cloisonnement Niveau 1 du Planning.

    L'utilisateur connecté est affecté uniquement au projet A.

    Le projet B appartient à un autre environnement client
    et ne doit jamais apparaître dans les différentes projections
    du Planning.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements clients
        # --------------------------------------------------------------

        cls.company_a = Company.objects.create(
            name="Société A - Planning",
        )

        cls.environment_a = ClientEnvironment.objects.create(
            company=cls.company_a,
        )

        cls.company_b = Company.objects.create(
            name="Société B - Planning",
        )

        cls.environment_b = ClientEnvironment.objects.create(
            company=cls.company_b,
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_PLAN_ACCESS_GLOBAL_ROLE",
            label="Rôle global test Planning",
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_PLAN_ACCESS_LEVEL",
            label="Niveau accès test Planning",
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company_a,
            email="planning-access@example.com",
            first_name="Jean",
            last_name="Planning",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.resource_a = User.objects.create(
            company=cls.company_a,
            email="planning-resource-a@example.com",
            first_name="Alice",
            last_name="Ressource A",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.resource_b = User.objects.create(
            company=cls.company_b,
            email="planning-resource-b@example.com",
            first_name="Bruno",
            last_name="Ressource B",
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
            code="TEST_PLAN_PROJECT_STATUS",
            label="Statut projet test Planning",
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
                code="TEST_PLAN_ACCESS_WP_STATUS",
                label="Statut lot test Planning",
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
        # Rôle d'affectation tâche
        # --------------------------------------------------------------

        cls.task_member_role_type = (
            CatalogType.objects.create(
                code="TASK_MEMBER_ROLE",
                label="Rôle membre tâche",
            )
        )

        cls.task_member_role = (
            CatalogValue.objects.create(
                catalog_type=(
                    cls.task_member_role_type
                ),
                code="MEMBER",
                label="Membre",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Projets
        #
        # Les deux projets utilisent volontairement la même période
        # afin que le filtre temporel ne puisse pas masquer un défaut
        # de cloisonnement.
        # --------------------------------------------------------------

        cls.project_a = Project.objects.create(
            company=cls.company_a,
            reference="PRJ-PLAN-A",
            name="Projet Planning A",
            status=cls.project_status,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-PLAN-B",
            name="Projet Planning B",
            status=cls.project_status,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        # --------------------------------------------------------------
        # Affectation projet
        #
        # L'utilisateur connecté n'est membre que du projet A.
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
            name="Lot Planning accessible A",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        cls.work_package_b = WorkPackage.objects.create(
            project=cls.project_b,
            status=cls.work_package_status,
            name="Lot Planning inaccessible B",
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
        )

        # --------------------------------------------------------------
        # Tâches
        # --------------------------------------------------------------

        cls.task_a = Task.objects.create(
            work_package=cls.work_package_a,
            status=cls.task_status,
            name="Tâche Planning accessible A",
            start_date=date(2026, 9, 7),
            end_date=date(2026, 9, 11),
        )

        cls.task_b = Task.objects.create(
            work_package=cls.work_package_b,
            status=cls.task_status,
            name="Tâche Planning inaccessible B",
            start_date=date(2026, 9, 7),
            end_date=date(2026, 9, 11),
        )

        # --------------------------------------------------------------
        # Affectations tâches
        # --------------------------------------------------------------

        cls.assignment_a = TaskAssignment.objects.create(
            task=cls.task_a,
            user=cls.resource_a,
            role=cls.task_member_role,
            allocation_percent=100,
        )

        cls.assignment_b = TaskAssignment.objects.create(
            task=cls.task_b,
            user=cls.resource_b,
            role=cls.task_member_role,
            allocation_percent=100,
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_planning_response(self, **parameters):
        data = {
            "state_date": "2026-09-10",
            "date_from": "2026-09-01",
            "date_to": "2026-09-30",
            "calendar_year": "2026",
            "calendar_month": "9",
        }

        data.update(parameters)

        return self.client.get(
            reverse("planning:home"),
            data=data,
        )

    # ------------------------------------------------------------------
    # Vue générale
    # ------------------------------------------------------------------

    def test_planning_returns_200(
        self,
    ):
        response = self.get_planning_response()

        self.assertEqual(
            response.status_code,
            200,
        )

    # ------------------------------------------------------------------
    # Sélecteur de projet
    # ------------------------------------------------------------------

    def test_project_selector_only_contains_accessible_projects(
        self,
    ):
        response = self.get_planning_response()

        self.assertEqual(
            response.status_code,
            200,
        )

        project_ids = set(
            response.context["projects"]
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

    # ------------------------------------------------------------------
    # Gantt
    # ------------------------------------------------------------------

    def test_gantt_only_contains_accessible_project_data(
        self,
    ):
        response = self.get_planning_response()

        planning = response.context["planning"]

        object_ids = {
            item.object_id
            for item in planning.items
        }

        self.assertIn(
            str(self.project_a.pk),
            object_ids,
        )

        self.assertIn(
            str(self.work_package_a.pk),
            object_ids,
        )

        self.assertIn(
            str(self.task_a.pk),
            object_ids,
        )

        self.assertNotIn(
            str(self.project_b.pk),
            object_ids,
        )

        self.assertNotIn(
            str(self.work_package_b.pk),
            object_ids,
        )

        self.assertNotIn(
            str(self.task_b.pk),
            object_ids,
        )

    # ------------------------------------------------------------------
    # Plan de charge
    # ------------------------------------------------------------------

    def test_workload_only_contains_accessible_project_resources(
        self,
    ):
        response = self.get_planning_response()

        workload = response.context["workload"]

        resource_ids = {
            resource.user_id
            for resource in workload.resources
        }

        self.assertIn(
            str(self.resource_a.pk),
            resource_ids,
        )

        self.assertNotIn(
            str(self.resource_b.pk),
            resource_ids,
        )

        visible_task_ids = {
            detail.task_id
            for resource in workload.resources
            for cell in resource.cells
            for detail in cell.details
        }

        self.assertIn(
            str(self.task_a.pk),
            visible_task_ids,
        )

        self.assertNotIn(
            str(self.task_b.pk),
            visible_task_ids,
        )

    # ------------------------------------------------------------------
    # Planning ressources
    # ------------------------------------------------------------------

    def test_resource_schedule_only_contains_accessible_project_data(
        self,
    ):
        response = self.get_planning_response()

        schedule = response.context[
            "resource_schedule"
        ]

        resource_ids = {
            resource.user_id
            for resource in schedule.resources
        }

        self.assertIn(
            str(self.resource_a.pk),
            resource_ids,
        )

        self.assertNotIn(
            str(self.resource_b.pk),
            resource_ids,
        )

        visible_task_ids = {
            assignment.task_id
            for resource in schedule.resources
            for assignment in resource.assignments
        }

        self.assertIn(
            str(self.task_a.pk),
            visible_task_ids,
        )

        self.assertNotIn(
            str(self.task_b.pk),
            visible_task_ids,
        )

    # ------------------------------------------------------------------
    # Calendrier
    # ------------------------------------------------------------------

    def test_calendar_only_contains_accessible_project_events(
        self,
    ):
        response = self.get_planning_response()

        calendar = response.context["calendar"]

        events = [
            event
            for week in calendar.weeks
            for day in week.days
            for event in day.events
        ]

        project_ids = {
            event.project_id
            for event in events
        }

        self.assertIn(
            str(self.project_a.pk),
            project_ids,
        )

        self.assertNotIn(
            str(self.project_b.pk),
            project_ids,
        )

        object_ids = {
            event.object_id
            for event in events
        }

        self.assertIn(
            str(self.task_a.pk),
            object_ids,
        )

        self.assertNotIn(
            str(self.task_b.pk),
            object_ids,
        )

    # ------------------------------------------------------------------
    # Projet explicitement sélectionné
    # ------------------------------------------------------------------

    def test_accessible_project_can_be_selected(
        self,
    ):
        response = self.get_planning_response(
            project=str(self.project_a.pk),
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context[
                "selected_project"
            ],
            self.project_a,
        )

    def test_inaccessible_project_returns_404(
        self,
    ):
        response = self.get_planning_response(
            project=str(self.project_b.pk),
        )

        self.assertEqual(
            response.status_code,
            404,
        )