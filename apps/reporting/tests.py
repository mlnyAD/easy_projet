

from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.projects.models import (
    Project,
    ProjectMembership,
)
from apps.reporting.models import (
    ActivityReport,
    ActivityReportEntry,
    ActivityReportLine,
    ActivityReportProjectReview,
)
from apps.tasks.models import Task
from apps.users.models import User
from apps.work.models import WorkPackage


@override_settings(
    DEV_AUTO_LOGIN=False,
)
class ActivityReportLevel1AccessTests(TestCase):
    """
    Tests de cloisonnement Niveau 1 du Reporting.

    Un même rapport hebdomadaire peut contenir :
    - des activités du projet B ;
    - des activités du projet C ;
    - des activités internes.

    Une review projet ne doit exposer que les
    activités appartenant au projet concerné.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés / environnements clients
        # --------------------------------------------------------------

        cls.company_b = Company.objects.create(
            name="Société cliente B",
        )

        cls.environment_b = (
            ClientEnvironment.objects.create(
                company=cls.company_b,
            )
        )

        cls.company_c = Company.objects.create(
            name="Société cliente C",
        )

        cls.environment_c = (
            ClientEnvironment.objects.create(
                company=cls.company_c,
            )
        )

        cls.company_employee = Company.objects.create(
            name="Société employeur A",
        )

        # --------------------------------------------------------------
        # Rôles globaux
        #
        # USER_GLOBAL_ROLE doit porter exactement ce code car
        # les services d'accès le contrôlent explicitement.
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="USER_GLOBAL_ROLE",
            label="Rôle global",
        )

        cls.project_manager_role = (
            CatalogValue.objects.create(
                catalog_type=cls.global_role_type,
                code="PROJECT_MANAGER",
                label="Chef de projet",
                sort_order=10,
            )
        )

        cls.user_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Niveau d'accès utilisateur
        # --------------------------------------------------------------

        cls.access_level_type = CatalogType.objects.create(
            code="TEST_REPORTING_ACCESS_LEVEL",
            label="Niveau accès Reporting",
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

        cls.report_user = User.objects.create(
            company=cls.company_employee,
            email="report-user@example.com",
            first_name="Paul",
            last_name="Rapport",
            global_role=cls.user_role,
            access_level=cls.access_level,
        )

        cls.manager_b = User.objects.create(
            company=cls.company_b,
            email="manager-b@example.com",
            first_name="Bruno",
            last_name="Manager",
            global_role=cls.project_manager_role,
            access_level=cls.access_level,
        )

        cls.manager_c = User.objects.create(
            company=cls.company_c,
            email="manager-c@example.com",
            first_name="Claire",
            last_name="Manager",
            global_role=cls.project_manager_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="TEST_REPORTING_PROJECT_STATUS",
            label="Statut projet Reporting",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
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
            code="PROJECT_MANAGER",
            label="Chef de projet",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Projets B et C
        # --------------------------------------------------------------

        cls.project_b = Project.objects.create(
            company=cls.company_b,
            reference="PRJ-REPORT-B",
            name="Projet Reporting B",
            status=cls.project_status,
            project_manager=cls.manager_b,
        )

        cls.project_c = Project.objects.create(
            company=cls.company_c,
            reference="PRJ-REPORT-C",
            name="Projet Reporting C",
            status=cls.project_status,
            project_manager=cls.manager_c,
        )

        # ProjectAccessService utilise les memberships
        # pour les utilisateurs non administrateurs.

        ProjectMembership.objects.create(
            project=cls.project_b,
            user=cls.manager_b,
            role=cls.project_role,
        )

        ProjectMembership.objects.create(
            project=cls.project_c,
            user=cls.manager_c,
            role=cls.project_role,
        )

        # --------------------------------------------------------------
        # Statut lot
        # --------------------------------------------------------------

        cls.work_package_status_type = (
            CatalogType.objects.create(
                code="TEST_REPORTING_WP_STATUS",
                label="Statut lot Reporting",
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
        # Lots B et C
        # --------------------------------------------------------------

        cls.work_package_b = WorkPackage.objects.create(
            project=cls.project_b,
            status=cls.work_package_status,
            name="Lot Reporting B",
        )

        cls.work_package_c = WorkPackage.objects.create(
            project=cls.project_c,
            status=cls.work_package_status,
            name="Lot Reporting C",
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
        # Tâches B et C
        # --------------------------------------------------------------

        cls.task_b = Task.objects.create(
            work_package=cls.work_package_b,
            status=cls.task_status,
            name="Tâche confidentielle projet B",
        )

        cls.task_c = Task.objects.create(
            work_package=cls.work_package_c,
            status=cls.task_status,
            name="Tâche confidentielle projet C",
        )

        # --------------------------------------------------------------
        # Statut du rapport
        # --------------------------------------------------------------

        cls.report_status_type = CatalogType.objects.create(
            code="ACTIVITY_REPORT",
            label="Rapport d'activité",
        )

        cls.submitted_status = CatalogValue.objects.create(
            catalog_type=cls.report_status_type,
            code="SUBMITTED",
            label="Transmis",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Type d'activité interne
        # --------------------------------------------------------------

        cls.line_type_catalog = CatalogType.objects.create(
            code="ACTIVITY_REPORT_LINE",
            label="Type activité rapport",
        )

        cls.internal_activity = (
            CatalogValue.objects.create(
                catalog_type=cls.line_type_catalog,
                code="TRAINING",
                label="Formation interne confidentielle",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Rapport hebdomadaire unique
        # --------------------------------------------------------------

        cls.week_start = date(
            2026,
            8,
            31,
        )

        cls.week_end = date(
            2026,
            9,
            6,
        )

        cls.report = ActivityReport.objects.create(
            user=cls.report_user,
            status=cls.submitted_status,
            period_start_date=cls.week_start,
            period_end_date=cls.week_end,
            global_comment="Rapport multi-projets",
        )

        # --------------------------------------------------------------
        # Ligne Projet B
        # --------------------------------------------------------------

        cls.line_b = ActivityReportLine.objects.create(
            activity_report=cls.report,
            task=cls.task_b,
        )

        ActivityReportEntry.objects.create(
            activity_report_line=cls.line_b,
            activity_date=date(
                2026,
                8,
                31,
            ),
            regular_hours=Decimal("4.00"),
            overtime_hours=Decimal("1.00"),
        )

        # --------------------------------------------------------------
        # Ligne Projet C
        # --------------------------------------------------------------

        cls.line_c = ActivityReportLine.objects.create(
            activity_report=cls.report,
            task=cls.task_c,
        )

        ActivityReportEntry.objects.create(
            activity_report_line=cls.line_c,
            activity_date=date(
                2026,
                9,
                1,
            ),
            regular_hours=Decimal("6.00"),
            overtime_hours=Decimal("2.00"),
        )

        # --------------------------------------------------------------
        # Activité interne
        # --------------------------------------------------------------

        cls.line_internal = (
            ActivityReportLine.objects.create(
                activity_report=cls.report,
                line_type=cls.internal_activity,
            )
        )

        ActivityReportEntry.objects.create(
            activity_report_line=cls.line_internal,
            activity_date=date(
                2026,
                9,
                2,
            ),
            regular_hours=Decimal("7.00"),
            overtime_hours=Decimal("3.00"),
        )

        # --------------------------------------------------------------
        # Reviews projet
        # --------------------------------------------------------------

        cls.review_b = (
            ActivityReportProjectReview.objects.create(
                activity_report=cls.report,
                project=cls.project_b,
            )
        )

        cls.review_c = (
            ActivityReportProjectReview.objects.create(
                activity_report=cls.report,
                project=cls.project_c,
            )
        )

    # ------------------------------------------------------------------
    # Détail Projet B
    # ------------------------------------------------------------------

    def test_review_b_returns_200_for_manager_b(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_review_b_contains_only_project_b_rows(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_b.pk,
                },
            )
        )

        rows = response.context[
            "report_rows"
        ]

        self.assertEqual(
            len(rows),
            1,
        )

        self.assertEqual(
            rows[0]["line"].pk,
            self.line_b.pk,
        )

        self.assertEqual(
            rows[0]["project"].pk,
            self.project_b.pk,
        )

    def test_review_b_excludes_project_c_line(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_b.pk,
                },
            )
        )

        line_ids = {
            row["line"].pk
            for row in response.context[
                "report_rows"
            ]
        }

        self.assertNotIn(
            self.line_c.pk,
            line_ids,
        )

    def test_review_b_excludes_internal_activity(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_b.pk,
                },
            )
        )

        line_ids = {
            row["line"].pk
            for row in response.context[
                "report_rows"
            ]
        }

        self.assertNotIn(
            self.line_internal.pk,
            line_ids,
        )

    # ------------------------------------------------------------------
    # Totaux Projet B
    # ------------------------------------------------------------------

    def test_review_b_totals_are_project_b_only(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_b.pk,
                },
            )
        )

        self.assertEqual(
            response.context["regular_total"],
            Decimal("4.00"),
        )

        self.assertEqual(
            response.context["overtime_total"],
            Decimal("1.00"),
        )

        self.assertEqual(
            response.context["week_total"],
            Decimal("5.00"),
        )

    # ------------------------------------------------------------------
    # Accès direct inter-projets
    # ------------------------------------------------------------------

    def test_manager_b_cannot_access_review_c_by_uuid(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-detail",
                kwargs={
                    "pk": self.review_c.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ------------------------------------------------------------------
    # Liste des reviews
    # ------------------------------------------------------------------

    def test_manager_b_review_list_contains_only_project_b(self):
        self.client.force_login(
            self.manager_b
        )

        response = self.client.get(
            reverse(
                "reporting:review-list",
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        reviews = list(
            response.context["reviews"]
        )

        review_ids = {
            review.pk
            for review in reviews
        }

        self.assertIn(
            self.review_b.pk,
            review_ids,
        )

        self.assertNotIn(
            self.review_c.pk,
            review_ids,
        )