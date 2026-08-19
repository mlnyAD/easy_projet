

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction

from apps.catalogs.models import CatalogValue
from apps.tasks.models import TaskAssignment
from apps.users.models import User

from apps.reporting.models import (
    ActivityReport,
    ActivityReportEntry,
    ActivityReportLine,
)


class ActivityReportPreparationError(Exception):
    """
    Erreur lors de la préparation d'un rapport d'activité.
    """


class ActivityReportPreparationService:
    """
    Création et synchronisation d'un rapport d'activité hebdomadaire.

    Principes :
    - le rapport est créé à sa première ouverture ;
    - un rapport DRAFT est enrichi à partir du planning courant ;
    - aucune ligne existante n'est supprimée automatiquement ;
    - aucune heure déjà saisie n'est modifiée ;
    - un rapport SUBMITTED n'est plus synchronisé.
    """

    REPORT_CATALOG_CODE = "ACTIVITY_REPORT"
    DRAFT_STATUS_CODE = "DRAFT"
    SUBMITTED_STATUS_CODE = "SUBMITTED"

    ZERO_HOURS = Decimal("0.00")

    @classmethod
    def prepare(
        cls,
        *,
        user: User,
        period_start_date: date,
    ) -> ActivityReport:
        """
        Retourne le rapport hebdomadaire de l'utilisateur.

        S'il n'existe pas, il est créé.

        Tant que le rapport est en brouillon, les tâches actuellement
        planifiées pour l'utilisateur pendant la semaine sont ajoutées
        si elles ne figurent pas encore dans le rapport.

        Les informations déjà saisies ne sont jamais supprimées
        ni remplacées.
        """

        cls._validate_period_start_date(
            period_start_date
        )

        period_end_date = (
            period_start_date
            + timedelta(days=6)
        )

        draft_status = cls._get_report_status(
            cls.DRAFT_STATUS_CODE
        )

        with transaction.atomic():

            report, _created = (
                ActivityReport.objects.get_or_create(
                    user=user,
                    period_start_date=period_start_date,
                    defaults={
                        "period_end_date": period_end_date,
                        "status": draft_status,
                    },
                )
            )

            report = (
                ActivityReport.objects
                .select_for_update()
                .select_related(
                    "status",
                    "status__catalog_type",
                )
                .get(pk=report.pk)
            )

            cls._validate_existing_report_period(
                report=report,
                expected_end_date=period_end_date,
            )

            if (
                report.status.code
                == cls.SUBMITTED_STATUS_CODE
            ):
                return report

            if (
                report.status.code
                != cls.DRAFT_STATUS_CODE
            ):
                raise ActivityReportPreparationError(
                    "Le rapport d'activité possède un statut "
                    "incompatible avec sa préparation."
                )

            cls._synchronize_task_lines(
                report=report,
            )

            cls._ensure_entries_for_all_lines(
                report=report,
            )

            return report

    # ------------------------------------------------------------------
    # Synchronisation des tâches
    # ------------------------------------------------------------------

    @classmethod
    def _synchronize_task_lines(
        cls,
        *,
        report: ActivityReport,
    ) -> None:
        """
        Ajoute au rapport les tâches actuellement affectées
        à l'utilisateur et intersectant la semaine du rapport.

        Aucune ligne existante n'est supprimée.
        """

        assignments = (
            TaskAssignment.objects
            .filter(
                user=report.user,
                is_active=True,
                task__is_active=True,
            )
            .select_related(
                "task",
                "task__work_package",
                "task__work_package__project",
            )
        )

        for assignment in assignments:
            task = assignment.task

            if not cls._task_intersects_report(
                task=task,
                report=report,
            ):
                continue

            ActivityReportLine.objects.get_or_create(
                activity_report=report,
                task=task,
                defaults={
                    "line_type": None,
                    "is_active": True,
                },
            )

    @staticmethod
    def _task_intersects_report(
        *,
        task,
        report: ActivityReport,
    ) -> bool:
        """
        Indique si la tâche intersecte la semaine du rapport.

        Une tâche sans dates exploitables n'est pas préremplie
        automatiquement.
        """

        task_start_date = (
            task.effective_start_date
        )

        task_end_date = (
            task.effective_end_date
        )

        if (
            task_start_date is None
            or task_end_date is None
        ):
            return False

        return (
            task_start_date
            <= report.period_end_date
            and task_end_date
            >= report.period_start_date
        )

    # ------------------------------------------------------------------
    # Entrées quotidiennes
    # ------------------------------------------------------------------

    @classmethod
    def _ensure_entries_for_all_lines(
        cls,
        *,
        report: ActivityReport,
    ) -> None:
        """
        Garantit sept entrées quotidiennes pour chaque ligne
        du rapport.

        Les entrées existantes ne sont jamais modifiées.
        """

        lines = (
            report.lines
            .filter(is_active=True)
            .all()
        )

        for line in lines:
            cls._ensure_line_entries(
                line=line,
                period_start_date=(
                    report.period_start_date
                ),
            )

    @classmethod
    def _ensure_line_entries(
        cls,
        *,
        line: ActivityReportLine,
        period_start_date: date,
    ) -> None:
        """
        Garantit une entrée du lundi au dimanche pour une ligne.
        """

        existing_dates = set(
            line.entries.values_list(
                "activity_date",
                flat=True,
            )
        )

        entries_to_create = []

        for day_offset in range(7):
            activity_date = (
                period_start_date
                + timedelta(days=day_offset)
            )

            if activity_date in existing_dates:
                continue

            entries_to_create.append(
                ActivityReportEntry(
                    activity_report_line=line,
                    activity_date=activity_date,
                    regular_hours=cls.ZERO_HOURS,
                    overtime_hours=cls.ZERO_HOURS,
                )
            )

        if entries_to_create:
            ActivityReportEntry.objects.bulk_create(
                entries_to_create,
                ignore_conflicts=True,
            )

    # ------------------------------------------------------------------
    # Statuts et période
    # ------------------------------------------------------------------

    @classmethod
    def _get_report_status(
        cls,
        status_code: str,
    ) -> CatalogValue:
        """
        Retourne un statut actif du catalogue ACTIVITY_REPORT.
        """

        status = (
            CatalogValue.objects
            .filter(
                catalog_type__code=(
                    cls.REPORT_CATALOG_CODE
                ),
                catalog_type__is_active=True,
                code=status_code,
                is_active=True,
            )
            .select_related(
                "catalog_type",
            )
            .first()
        )

        if status is None:
            raise ActivityReportPreparationError(
                "Le statut "
                f"{status_code!r} "
                "du catalogue ACTIVITY_REPORT "
                "n'est pas configuré."
            )

        return status

    @staticmethod
    def _validate_period_start_date(
        period_start_date: date,
    ) -> None:
        """
        Une période hebdomadaire commence obligatoirement un lundi.
        """

        if period_start_date.weekday() != 0:
            raise ActivityReportPreparationError(
                "La période du rapport d'activité "
                "doit commencer un lundi."
            )

    @staticmethod
    def _validate_existing_report_period(
        *,
        report: ActivityReport,
        expected_end_date: date,
    ) -> None:
        """
        Vérifie la cohérence d'un rapport déjà existant.
        """

        if (
            report.period_end_date
            != expected_end_date
        ):
            raise ActivityReportPreparationError(
                "La période du rapport d'activité existant "
                "est incohérente."
            )