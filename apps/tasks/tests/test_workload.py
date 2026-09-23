from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.licenses.models import ClientEnvironment
from apps.projects.models import Project
from apps.reporting.models import (
    ActivityReport,
    ActivityReportEntry,
    ActivityReportLine,
    ActivityReportProjectReview,
    ActivityReportProjectReviewStatus,
)
from apps.tasks.models import Task
from apps.tasks.services import TaskWorkloadService
from apps.users.models import User
from apps.work.models import WorkPackage


class TaskWorkloadServiceTests(TestCase):
    """
    Tests de remontée des heures validées vers les tâches.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test consommé",
        )

        ClientEnvironment.objects.create(
            company=cls.company,
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="workload-user@example.com",
            first_name="Jean",
            last_name="Consommé",
        )

        cls.project_status = cls._create_catalog_value(
            catalog_code="TEST_WORKLOAD_PROJECT_STATUS",
            value_code="IN_PROGRESS",
            label="En cours",
        )
        cls.work_package_status = cls._create_catalog_value(
            catalog_code="TEST_WORKLOAD_WP_STATUS",
            value_code="IN_PROGRESS",
            label="En cours",
        )
        cls.task_status = cls._create_catalog_value(
            catalog_code="TEST_WORKLOAD_TASK_STATUS",
            value_code="PLANNED",
            label="Planifiée",
        )
        cls.report_status = cls._create_catalog_value(
            catalog_code="ACTIVITY_REPORT",
            value_code="DRAFT",
            label="Brouillon",
        )

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-WORKLOAD-001",
            name="Projet consommé",
            status=cls.project_status,
        )
        cls.work_package = WorkPackage.objects.create(
            project=cls.project,
            status=cls.work_package_status,
            name="Lot consommé",
        )

    @classmethod
    def _create_catalog_value(
        cls,
        *,
        catalog_code,
        value_code,
        label,
    ):
        catalog_type = CatalogType.objects.create(
            code=catalog_code,
            label=catalog_code,
        )

        return CatalogValue.objects.create(
            catalog_type=catalog_type,
            code=value_code,
            label=label,
            sort_order=10,
        )

    def _create_report_line(self, *, task):
        report = ActivityReport.objects.create(
            user=self.user,
            status=self.report_status,
            period_start_date=date(2026, 9, 14),
            period_end_date=date(2026, 9, 20),
        )

        return (
            report,
            ActivityReportLine.objects.create(
                activity_report=report,
                task=task,
            ),
        )

    def test_validated_hours_update_automatic_indicators_only(self):
        task = Task.objects.create(
            work_package=self.work_package,
            status=self.task_status,
            name="Tâche avec charge réalisée",
            planned_workload_hours=20,
            remaining_workload_hours=20,
            progress_percent=0,
        )
        report, line = self._create_report_line(task=task)

        ActivityReportEntry.objects.create(
            activity_report_line=line,
            activity_date=date(2026, 9, 15),
            regular_hours=Decimal("2.00"),
            overtime_hours=Decimal("0.25"),
        )
        review = ActivityReportProjectReview.objects.create(
            activity_report=report,
            project=self.project,
            status=ActivityReportProjectReviewStatus.PENDING,
        )

        TaskWorkloadService.synchronize_project(
            project=self.project,
        )
        task.refresh_from_db()

        self.assertEqual(
            task.remaining_workload_hours,
            Decimal("20.00"),
        )
        self.assertEqual(task.progress_percent, 0)

        review.status = ActivityReportProjectReviewStatus.VALIDATED
        review.save(update_fields=["status"])

        TaskWorkloadService.synchronize_project(
            project=self.project,
        )
        task.refresh_from_db()

        self.assertEqual(
            task.remaining_workload_hours,
            Decimal("17.75"),
        )
        self.assertEqual(task.progress_percent, 11)

        task.remaining_workload_hours = Decimal("5.00")
        task.remaining_workload_hours_is_manual = True
        task.progress_percent = 40
        task.progress_percent_is_manual = True
        task.save()

        ActivityReportEntry.objects.create(
            activity_report_line=line,
            activity_date=date(2026, 9, 16),
            regular_hours=Decimal("2.00"),
            overtime_hours=Decimal("0.00"),
        )

        TaskWorkloadService.synchronize_project(
            project=self.project,
        )
        task.refresh_from_db()

        self.assertEqual(
            task.remaining_workload_hours,
            Decimal("5.00"),
        )
        self.assertEqual(task.progress_percent, 40)
