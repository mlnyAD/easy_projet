

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.tasks.models import (
    Task,
    TaskAssignment,
    TaskDependency,
)
from apps.users.models import User
from apps.work.models import WorkPackage


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class TaskViewTests(TestCase):
    """
    Tests d'intégration des vues de formulaire Tâche.

    Ces tests vérifient notamment l'utilisation du formulaire
    générique EDF et la présence des collections génériques
    Personnel et Enchaînements.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société et environnement
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test vues tâches",
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
            code="TEST_TASK_VIEW_USER_ROLE",
            label="Rôle global test vues tâches",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_TASK_VIEW_ACCESS_LEVEL",
            label="Niveau accès test vues tâches",
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

        cls.user = User.objects.create(
            company=cls.company,
            email="task-view@example.com",
            first_name="Jean",
            last_name="Tâche",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.assigned_user = User.objects.create(
            company=cls.company,
            email="task-assigned@example.com",
            first_name="Paul",
            last_name="Affecté",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_TASK_VIEW_PROJECT_STATUS",
            label="Statut projet test vues tâches",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut lot
        # --------------------------------------------------------------

        cls.work_package_status_type = CatalogType.objects.create(
            code="TEST_TASK_VIEW_WP_STATUS",
            label="Statut lot test vues tâches",
        )

        cls.work_package_status = CatalogValue.objects.create(
            catalog_type=cls.work_package_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Catalogue TASK_STATUS
        #
        # Le code doit être exactement TASK_STATUS car TaskForm
        # recherche explicitement ce catalogue.
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
        # Catalogue TASK_MEMBER_ROLE
        #
        # Même principe : TaskAssignmentForm recherche explicitement
        # TASK_MEMBER_ROLE.
        # --------------------------------------------------------------

        cls.task_member_role_type = CatalogType.objects.create(
            code="TASK_MEMBER_ROLE",
            label="Rôle sur tâche",
        )

        cls.task_member_role = CatalogValue.objects.create(
            catalog_type=cls.task_member_role_type,
            code="WORKER",
            label="Intervenant",
            sort_order=10,
            is_default=True,
        )

        # --------------------------------------------------------------
        # Catalogue USER_PROJECT_ROLE
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
        # Projet
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-TASK-VIEW-001",
            name="Projet vues tâches",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Affectations projet
        # --------------------------------------------------------------

        ProjectMembership.objects.create(
            project=cls.project,
            user=cls.user,
            role=cls.project_role,
        )

        ProjectMembership.objects.create(
            project=cls.project,
            user=cls.assigned_user,
            role=cls.project_role,
        )

        # --------------------------------------------------------------
        # Lot
        # --------------------------------------------------------------

        cls.work_package = WorkPackage.objects.create(
            project=cls.project,
            status=cls.work_package_status,
            name="Lot test vues tâches",
        )

        # --------------------------------------------------------------
        # Tâches
        # --------------------------------------------------------------

        cls.predecessor = Task.objects.create(
            work_package=cls.work_package,
            status=cls.task_status,
            name="Tâche antécédente",
        )

        cls.task = Task.objects.create(
            work_package=cls.work_package,
            status=cls.task_status,
            name="Tâche à modifier",
        )

        # --------------------------------------------------------------
        # Collections existantes
        # --------------------------------------------------------------

        cls.assignment = TaskAssignment.objects.create(
            task=cls.task,
            user=cls.assigned_user,
            role=cls.task_member_role,
            allocation_percent=50,
        )

        cls.dependency = TaskDependency.objects.create(
            predecessor=cls.predecessor,
            successor=cls.task,
        )

    def setUp(self):
        self.client.force_login(
            self.user
        )

    def get_collection(
        self,
        response,
        name,
    ):
        for collection in (
            response.context[
                "form_view"
            ].collections
        ):
            if collection.name == name:
                return collection

        self.fail(
            f"Collection {name!r} introuvable."
        )
    
    # ------------------------------------------------------------------
    # Création
    # ------------------------------------------------------------------

    def test_create_page_returns_200(self):
        response = self.client.get(
            reverse(
                "tasks:create",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_create_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            reverse(
                "tasks:create",
            )
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_create_page_contains_assignments_collection(self):
        response = self.client.get(
            reverse(
                "tasks:create",
            )
        )

        collections = {
            collection.name
            for collection
            in response.context["form_view"].collections
        }

        self.assertIn(
            "assignments",
            collections,
        )

    def test_create_page_contains_dependencies_collection(self):
        response = self.client.get(
            reverse(
                "tasks:create",
            )
        )

        collections = {
            collection.name
            for collection
            in response.context["form_view"].collections
        }

        self.assertIn(
            "dependencies",
            collections,
        )

    def test_create_page_renders_collection_management_forms(self):
        response = self.client.get(
            reverse(
                "tasks:create",
            )
        )

        self.assertContains(
            response,
            'name="assignments-TOTAL_FORMS"',
        )

        self.assertContains(
            response,
            'name="dependencies-TOTAL_FORMS"',
        )

    # ------------------------------------------------------------------
    # Modification
    # ------------------------------------------------------------------

    def test_update_page_returns_200(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_update_page_uses_generic_edf_form_template(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        self.assertTemplateUsed(
            response,
            "edf/form/view.html",
        )

    def test_update_page_contains_both_collections(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        collections = {
            collection.name
            for collection
            in response.context["form_view"].collections
        }

        self.assertEqual(
            collections,
            {
                "assignments",
                "dependencies",
            },
        )

    def test_update_page_contains_existing_assignment(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        collection = self.get_collection(
            response,
            "assignments",
        )

        self.assertEqual(
            len(collection.rows),
            1,
        )

        self.assertEqual(
            collection.rows[0].django_form.instance,
            self.assignment,
        )


    def test_update_page_contains_existing_dependency(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        collection = self.get_collection(
            response,
            "dependencies",
        )

        self.assertEqual(
            len(collection.rows),
            1,
        )

        self.assertEqual(
            collection.rows[0].django_form.instance,
            self.dependency,
        )


    def test_assignment_user_queryset_is_limited_to_project_members(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        collection = self.get_collection(
            response,
            "assignments",
        )

        queryset = (
            collection
            .rows[0]
            .django_form
            .fields["user"]
            .queryset
        )

        self.assertIn(
            self.assigned_user,
            queryset,
        )


    def test_dependency_queryset_excludes_current_task(self):
        response = self.client.get(
            reverse(
                "tasks:update",
                kwargs={
                    "pk": self.task.pk,
                },
            )
        )

        collection = self.get_collection(
            response,
            "dependencies",
        )

        queryset = (
            collection
            .rows[0]
            .django_form
            .fields["predecessor"]
            .queryset
        )

        self.assertIn(
            self.predecessor,
            queryset,
        )

        self.assertNotIn(
            self.task,
            queryset,
        )
        
    def test_update_can_add_assignment(self):
        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel
            "assignments-TOTAL_FORMS": "2",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "50",
            "assignments-0-is_active": "on",

            "assignments-1-id": "",
            "assignments-1-task": str(
                self.task.pk
            ),
            "assignments-1-user": str(
                self.user.pk
            ),
            "assignments-1-role": str(
                self.task_member_role.pk
            ),
            "assignments-1-allocation_percent": "75",
            "assignments-1-is_active": "on",

            # Enchaînements
            "dependencies-TOTAL_FORMS": "1",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                self.dependency.dependency_type
            ),
            "dependencies-0-lag_days": (
                self.dependency.lag_days
            ),
            "dependencies-0-is_active": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        assignment = (
            TaskAssignment.objects.get(
                task=self.task,
                user=self.user,
            )
        )

        self.assertEqual(
            assignment.role,
            self.task_member_role,
        )

        self.assertEqual(
            assignment.allocation_percent,
            75,
        )

        self.assertTrue(
            assignment.is_active
        )

    def test_update_can_modify_assignment(self):
        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel
            "assignments-TOTAL_FORMS": "1",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "80",
            "assignments-0-is_active": "on",

            # Enchaînements
            "dependencies-TOTAL_FORMS": "1",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                self.dependency.dependency_type
            ),
            "dependencies-0-lag_days": (
                self.dependency.lag_days
            ),
            "dependencies-0-is_active": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assignment.refresh_from_db()

        self.assertEqual(
            self.assignment.allocation_percent,
            80,
        )

        self.assertEqual(
            TaskAssignment.objects.filter(
                task=self.task,
            ).count(),
            1,
        )
        
    def test_update_can_delete_assignment(self):
        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel
            "assignments-TOTAL_FORMS": "1",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "50",
            "assignments-0-is_active": "on",
            "assignments-0-DELETE": "on",

            # Enchaînements inchangés
            "dependencies-TOTAL_FORMS": "1",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                self.dependency.dependency_type
            ),
            "dependencies-0-lag_days": (
                self.dependency.lag_days
            ),
            "dependencies-0-is_active": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            TaskAssignment.objects.filter(
                pk=self.assignment.pk,
            ).exists()
        )

        self.assertTrue(
            TaskDependency.objects.filter(
                pk=self.dependency.pk,
            ).exists()
        )
        
    def test_update_can_add_dependency(self):
        new_predecessor = Task.objects.create(
            work_package=self.work_package,
            status=self.task_status,
            name="Nouvelle tâche antécédente",
        )

        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel inchangé
            "assignments-TOTAL_FORMS": "1",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "50",
            "assignments-0-is_active": "on",

            # Enchaînements
            "dependencies-TOTAL_FORMS": "2",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            # Dépendance existante
            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                self.dependency.dependency_type
            ),
            "dependencies-0-lag_days": (
                self.dependency.lag_days
            ),
            "dependencies-0-is_active": "on",

            # Nouvelle dépendance
            "dependencies-1-id": "",
            "dependencies-1-successor": str(
                self.task.pk
            ),
            "dependencies-1-predecessor": str(
                new_predecessor.pk
            ),
            "dependencies-1-dependency_type": (
                TaskDependency
                .DependencyType
                .FINISH_TO_START
            ),
            "dependencies-1-lag_days": "2",
            "dependencies-1-is_active": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        dependency = TaskDependency.objects.get(
            predecessor=new_predecessor,
            successor=self.task,
        )

        self.assertEqual(
            dependency.dependency_type,
            TaskDependency.DependencyType.FINISH_TO_START,
        )

        self.assertEqual(
            dependency.lag_days,
            2,
        )

        self.assertTrue(
            dependency.is_active
        )

        self.assertEqual(
            TaskDependency.objects.filter(
                successor=self.task,
            ).count(),
            2,
        )
        
    def test_update_can_modify_dependency(self):
        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel inchangé
            "assignments-TOTAL_FORMS": "1",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "50",
            "assignments-0-is_active": "on",

            # Enchaînement modifié
            "dependencies-TOTAL_FORMS": "1",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                TaskDependency
                .DependencyType
                .START_TO_START
            ),
            "dependencies-0-lag_days": "3",
            "dependencies-0-is_active": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.dependency.refresh_from_db()

        self.assertEqual(
            self.dependency.dependency_type,
            TaskDependency.DependencyType.START_TO_START,
        )

        self.assertEqual(
            self.dependency.lag_days,
            3,
        )

        self.assertEqual(
            TaskDependency.objects.filter(
                successor=self.task,
            ).count(),
            1,
        )
        
    def test_update_can_delete_dependency(self):
        url = reverse(
            "tasks:update",
            kwargs={
                "pk": self.task.pk,
            },
        )

        data = {
            # Tâche
            "work_package": str(
                self.work_package.pk
            ),
            "status": str(
                self.task_status.pk
            ),
            "code": self.task.code,
            "name": self.task.name,
            "description": self.task.description,
            "initial_start_date": "",
            "initial_end_date": "",
            "start_date": "",
            "end_date": "",
            "planned_workload_hours": (
                self.task.planned_workload_hours
            ),
            "remaining_workload_hours": (
                self.task.remaining_workload_hours
            ),
            "progress_percent": (
                self.task.progress_percent
            ),
            "is_active": "on",

            # Personnel inchangé
            "assignments-TOTAL_FORMS": "1",
            "assignments-INITIAL_FORMS": "1",
            "assignments-MIN_NUM_FORMS": "0",
            "assignments-MAX_NUM_FORMS": "1000",

            "assignments-0-id": str(
                self.assignment.pk
            ),
            "assignments-0-task": str(
                self.task.pk
            ),
            "assignments-0-user": str(
                self.assigned_user.pk
            ),
            "assignments-0-role": str(
                self.task_member_role.pk
            ),
            "assignments-0-allocation_percent": "50",
            "assignments-0-is_active": "on",

            # Enchaînement supprimé
            "dependencies-TOTAL_FORMS": "1",
            "dependencies-INITIAL_FORMS": "1",
            "dependencies-MIN_NUM_FORMS": "0",
            "dependencies-MAX_NUM_FORMS": "1000",

            "dependencies-0-id": str(
                self.dependency.pk
            ),
            "dependencies-0-successor": str(
                self.task.pk
            ),
            "dependencies-0-predecessor": str(
                self.predecessor.pk
            ),
            "dependencies-0-dependency_type": (
                self.dependency.dependency_type
            ),
            "dependencies-0-lag_days": (
                self.dependency.lag_days
            ),
            "dependencies-0-is_active": "on",
            "dependencies-0-DELETE": "on",
        }

        response = self.client.post(
            url,
            data=data,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            TaskDependency.objects.filter(
                pk=self.dependency.pk,
            ).exists()
        )

        self.assertTrue(
            TaskAssignment.objects.filter(
                pk=self.assignment.pk,
            ).exists()
        )