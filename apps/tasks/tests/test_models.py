

from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from apps.licenses.models import ClientEnvironment
from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.projects.models import Project
from apps.tasks.models import (
    Task,
    TaskAssignment,
    TaskDependency,
)
from apps.users.models import User
from apps.work.models import WorkPackage


class TaskModelTests(TestCase):
    """
    Tests métier des tâches, affectations et dépendances.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test tâches",
        )
        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="TEST_TASK_USER_ROLE",
            label="Rôle global test tâches",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_TASK_ACCESS_LEVEL",
            label="Niveau accès test tâches",
        )

        cls.global_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
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

        cls.user_1 = User.objects.create(
            company=cls.company,
            email="task-user-1@example.com",
            first_name="Jean",
            last_name="Tâche",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.user_2 = User.objects.create(
            company=cls.company,
            email="task-user-2@example.com",
            first_name="Paul",
            last_name="Tâche",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statuts projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_TASK_PROJECT_STATUS",
            label="Statut projet test tâches",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statuts lot
        # --------------------------------------------------------------

        cls.work_package_status_type = CatalogType.objects.create(
            code="TEST_TASK_WP_STATUS",
            label="Statut lot test tâches",
        )

        cls.work_package_status = CatalogValue.objects.create(
            catalog_type=cls.work_package_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statuts tâche
        # --------------------------------------------------------------

        cls.task_status_type = CatalogType.objects.create(
            code="TEST_TASK_STATUS",
            label="Statut tâche test",
        )

        cls.task_status = CatalogValue.objects.create(
            catalog_type=cls.task_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Rôles sur tâche
        # --------------------------------------------------------------

        cls.assignment_role_type = CatalogType.objects.create(
            code="TEST_TASK_ASSIGNMENT_ROLE",
            label="Rôle affectation test",
        )

        cls.assignment_role = CatalogValue.objects.create(
            catalog_type=cls.assignment_role_type,
            code="WORKER",
            label="Intervenant",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project_1 = Project.objects.create(
            company=cls.company,
            reference="PRJ-TASK-001",
            name="Projet tâches 1",
            status=cls.project_status,
        )

        cls.project_2 = Project.objects.create(
            company=cls.company,
            reference="PRJ-TASK-002",
            name="Projet tâches 2",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Lots
        # --------------------------------------------------------------

        cls.work_package_1 = WorkPackage.objects.create(
            project=cls.project_1,
            status=cls.work_package_status,
            name="Lot test 1",
        )

        cls.work_package_2 = WorkPackage.objects.create(
            project=cls.project_2,
            status=cls.work_package_status,
            name="Lot test 2",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_task(
        self,
        *,
        work_package=None,
        name="Tâche test",
    ):
        return Task.objects.create(
            work_package=(
                work_package
                or self.work_package_1
            ),
            status=self.task_status,
            name=name,
        )

    # ------------------------------------------------------------------
    # Task
    # ------------------------------------------------------------------

    def test_task_name_is_trimmed_on_save(self):
        task = Task.objects.create(
            work_package=self.work_package_1,
            status=self.task_status,
            name="  Tâche avec espaces  ",
        )

        self.assertEqual(
            task.name,
            "Tâche avec espaces",
        )

    def test_task_code_is_generated(self):
        task = self.create_task()

        self.assertTrue(
            task.code
        )

        self.assertTrue(
            task.code.startswith(
                f"TSK_{self.work_package_1.code}"
            )
        )

    def test_task_current_dates_are_initialized_from_initial_dates(self):
        task = Task.objects.create(
            work_package=self.work_package_1,
            status=self.task_status,
            name="Tâche planifiée",
            initial_start_date=date(
                2026,
                9,
                1,
            ),
            initial_end_date=date(
                2026,
                9,
                15,
            ),
        )

        self.assertEqual(
            task.start_date,
            task.initial_start_date,
        )

        self.assertEqual(
            task.end_date,
            task.initial_end_date,
        )

    def test_task_rejects_invalid_initial_dates(self):
        task = Task(
            work_package=self.work_package_1,
            status=self.task_status,
            name="Tâche dates initiales invalides",
            initial_start_date=date(
                2026,
                9,
                10,
            ),
            initial_end_date=date(
                2026,
                9,
                1,
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            task.full_clean()

    def test_task_rejects_invalid_current_dates(self):
        task = Task(
            work_package=self.work_package_1,
            status=self.task_status,
            name="Tâche dates invalides",
            start_date=date(
                2026,
                9,
                10,
            ),
            end_date=date(
                2026,
                9,
                1,
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            task.full_clean()

    def test_task_rejects_progress_above_maximum(self):
        task = Task(
            work_package=self.work_package_1,
            status=self.task_status,
            name="Tâche avancement invalide",
            progress_percent=101,
        )

        with self.assertRaises(
            ValidationError
        ):
            task.full_clean()

    # ------------------------------------------------------------------
    # TaskAssignment
    # ------------------------------------------------------------------

    def test_task_assignment_accepts_valid_allocation(self):
        task = self.create_task()

        assignment = TaskAssignment(
            task=task,
            user=self.user_1,
            role=self.assignment_role,
            allocation_percent=50,
        )

        assignment.full_clean()

    def test_task_assignment_rejects_allocation_above_maximum(self):
        task = self.create_task()

        assignment = TaskAssignment(
            task=task,
            user=self.user_1,
            role=self.assignment_role,
            allocation_percent=101,
        )

        with self.assertRaises(
            ValidationError
        ):
            assignment.full_clean()

    def test_task_assignment_user_is_unique_per_task(self):
        task = self.create_task()

        TaskAssignment.objects.create(
            task=task,
            user=self.user_1,
            role=self.assignment_role,
            allocation_percent=50,
        )

        with self.assertRaises(
            IntegrityError
        ):
            TaskAssignment.objects.create(
                task=task,
                user=self.user_1,
                role=self.assignment_role,
                allocation_percent=25,
            )

    # ------------------------------------------------------------------
    # TaskDependency
    # ------------------------------------------------------------------

    def test_task_dependency_accepts_same_project(self):
        predecessor = self.create_task(
            name="Tâche antécédente",
        )

        successor = self.create_task(
            name="Tâche successeure",
        )

        dependency = TaskDependency(
            predecessor=predecessor,
            successor=successor,
        )

        dependency.full_clean()

    def test_task_dependency_rejects_self_dependency(self):
        task = self.create_task()

        dependency = TaskDependency(
            predecessor=task,
            successor=task,
        )

        with self.assertRaises(
            ValidationError
        ):
            dependency.full_clean()

    def test_task_dependency_rejects_different_projects(self):
        predecessor = self.create_task(
            work_package=self.work_package_1,
            name="Tâche projet 1",
        )

        successor = self.create_task(
            work_package=self.work_package_2,
            name="Tâche projet 2",
        )

        dependency = TaskDependency(
            predecessor=predecessor,
            successor=successor,
        )

        with self.assertRaises(
            ValidationError
        ):
            dependency.full_clean()

    def test_task_dependency_rejects_cycle(self):
        task_a = self.create_task(
            name="Tâche A",
        )

        task_b = self.create_task(
            name="Tâche B",
        )

        task_c = self.create_task(
            name="Tâche C",
        )

        TaskDependency.objects.create(
            predecessor=task_a,
            successor=task_b,
        )

        TaskDependency.objects.create(
            predecessor=task_b,
            successor=task_c,
        )

        dependency = TaskDependency(
            predecessor=task_c,
            successor=task_a,
        )

        with self.assertRaises(
            ValidationError
        ):
            dependency.full_clean()

    def test_task_dependency_pair_is_unique(self):
        predecessor = self.create_task(
            name="Tâche antécédente unique",
        )

        successor = self.create_task(
            name="Tâche successeure unique",
        )

        TaskDependency.objects.create(
            predecessor=predecessor,
            successor=successor,
        )

        with self.assertRaises(
            IntegrityError
        ):
            TaskDependency.objects.create(
                predecessor=predecessor,
                successor=successor,
            )