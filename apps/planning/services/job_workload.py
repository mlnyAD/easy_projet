

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from apps.projects.models import Project
from apps.tasks.models import TaskJobRequirement


@dataclass(frozen=True)
class JobWorkloadWeek:
    """
    Semaine affichée dans le plan de charge par métier.
    """

    start_date: date
    end_date: date
    label: str


@dataclass(frozen=True)
class JobWorkloadCell:
    """
    Répartition hebdomadaire d'un besoin métier.
    """

    week: JobWorkloadWeek
    planned_workload_hours: Decimal


@dataclass(frozen=True)
class JobWorkloadRequirement:
    """
    Ligne du plan de charge métier pour une tâche.
    """

    requirement_id: str
    project_reference: str
    project_name: str
    task_id: str
    task_code: str
    task_name: str
    job_label: str
    planned_workload_hours: Decimal
    visible_workload_hours: Decimal
    cells: tuple[JobWorkloadCell, ...]


@dataclass(frozen=True)
class JobWorkloadPlan:
    """
    Plan de charge hebdomadaire des besoins métiers.
    """

    date_from: date
    date_to: date
    weeks: tuple[JobWorkloadWeek, ...]
    requirements: tuple[JobWorkloadRequirement, ...]


class WeeklyJobWorkloadService:
    """
    Construit le plan de charge prévisionnel par métier et par tâche.

    Les heures prévues sont réparties proportionnellement aux jours
    ouvrés de chaque semaine de la tâche. Cette charge reste
    indépendante des affectations nominatives.
    """

    ZERO_HOURS = Decimal("0.00")
    HOUR_QUANTUM = Decimal("0.01")

    def build(
        self,
        *,
        date_from: date,
        date_to: date,
        project: Project | None = None,
        accessible_projects,
    ) -> JobWorkloadPlan:
        """
        Construit le plan de charge métier sur la période demandée.
        """

        if date_to < date_from:
            raise ValueError(
                "La date de fin ne peut pas être antérieure "
                "à la date de début."
            )

        weeks = self._build_weeks(
            date_from=date_from,
            date_to=date_to,
        )

        requirements = self._get_requirements(
            date_from=date_from,
            date_to=date_to,
            project=project,
            accessible_projects=accessible_projects,
        )

        rows = tuple(
            self._build_requirement(
                requirement=requirement,
                weeks=weeks,
            )
            for requirement in requirements
        )

        return JobWorkloadPlan(
            date_from=date_from,
            date_to=date_to,
            weeks=weeks,
            requirements=rows,
        )

    @staticmethod
    def _get_requirements(
        *,
        date_from: date,
        date_to: date,
        project: Project | None,
        accessible_projects,
    ):
        """
        Retourne les besoins métiers actifs dont la tâche intersecte
        la période affichée.
        """

        queryset = (
            TaskJobRequirement.objects
            .filter(
                task__work_package__project__in=accessible_projects,
                is_active=True,
                task__is_active=True,
                task__start_date__isnull=False,
                task__end_date__isnull=False,
                task__start_date__lte=date_to,
                task__end_date__gte=date_from,
            )
            .select_related(
                "job",
                "task",
                "task__work_package",
                "task__work_package__project",
            )
            .order_by(
                "task__work_package__project__reference",
                "task__start_date",
                "task__code",
                "job__sort_order",
                "job__label",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                task__work_package__project=project,
            )

        return queryset

    def _build_requirement(
        self,
        *,
        requirement: TaskJobRequirement,
        weeks: tuple[JobWorkloadWeek, ...],
    ) -> JobWorkloadRequirement:
        """
        Construit une ligne métier et sa répartition hebdomadaire.
        """

        task = requirement.task

        task_working_days = self._count_working_days(
            start_date=task.start_date,
            end_date=task.end_date,
        )

        cells = tuple(
            self._build_cell(
                requirement=requirement,
                week=week,
                task_working_days=task_working_days,
            )
            for week in weeks
        )

        visible_workload_hours = sum(
            (
                cell.planned_workload_hours
                for cell in cells
            ),
            self.ZERO_HOURS,
        ).quantize(self.HOUR_QUANTUM)

        project = task.work_package.project

        return JobWorkloadRequirement(
            requirement_id=str(requirement.pk),
            project_reference=project.reference,
            project_name=project.name,
            task_id=str(task.pk),
            task_code=task.code,
            task_name=task.name,
            job_label=requirement.job.label,
            planned_workload_hours=Decimal(
                requirement.planned_workload_hours
            ).quantize(self.HOUR_QUANTUM),
            visible_workload_hours=visible_workload_hours,
            cells=cells,
        )

    def _build_cell(
        self,
        *,
        requirement: TaskJobRequirement,
        week: JobWorkloadWeek,
        task_working_days: int,
    ) -> JobWorkloadCell:
        """
        Répartit les heures du besoin sur une semaine.
        """

        task = requirement.task

        if (
            task_working_days == 0
            or not self._intersects(
                start_date=task.start_date,
                end_date=task.end_date,
                period_start=week.start_date,
                period_end=week.end_date,
            )
        ):
            return JobWorkloadCell(
                week=week,
                planned_workload_hours=self.ZERO_HOURS,
            )

        visible_start = max(
            task.start_date,
            week.start_date,
        )

        visible_end = min(
            task.end_date,
            week.end_date,
        )

        covered_working_days = self._count_working_days(
            start_date=visible_start,
            end_date=visible_end,
        )

        planned_workload_hours = (
            Decimal(requirement.planned_workload_hours)
            * Decimal(covered_working_days)
            / Decimal(task_working_days)
        ).quantize(self.HOUR_QUANTUM)

        return JobWorkloadCell(
            week=week,
            planned_workload_hours=planned_workload_hours,
        )

    @staticmethod
    def _build_weeks(
        *,
        date_from: date,
        date_to: date,
    ) -> tuple[JobWorkloadWeek, ...]:
        """
        Construit les semaines ISO intersectant la période.
        """

        weeks: list[JobWorkloadWeek] = []

        current = (
            date_from
            - timedelta(days=date_from.weekday())
        )

        while current <= date_to:
            week_end = current + timedelta(days=6)
            _iso_year, iso_week, _iso_day = current.isocalendar()

            weeks.append(
                JobWorkloadWeek(
                    start_date=current,
                    end_date=week_end,
                    label=f"S{iso_week:02d}",
                )
            )

            current += timedelta(days=7)

        return tuple(weeks)

    @staticmethod
    def _count_working_days(
        *,
        start_date: date,
        end_date: date,
    ) -> int:
        """
        Compte les jours ouvrés du lundi au vendredi.
        """

        if end_date < start_date:
            return 0

        current = start_date
        count = 0

        while current <= end_date:
            if current.weekday() < 5:
                count += 1

            current += timedelta(days=1)

        return count

    @staticmethod
    def _intersects(
        *,
        start_date: date,
        end_date: date,
        period_start: date,
        period_end: date,
    ) -> bool:
        return (
            start_date <= period_end
            and end_date >= period_start
        )
