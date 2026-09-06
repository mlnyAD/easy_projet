

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from apps.tasks.models import TaskAssignment
from apps.users.models import User


@dataclass(frozen=True)
class WorkloadWeek:
    """
    Semaine affichée dans le plan de charge.
    """

    start_date: date
    end_date: date
    label: str


@dataclass(frozen=True)
class WorkloadTaskDetail:
    """
    Contribution d'une tâche à la charge hebdomadaire
    d'une ressource.
    """

    task_id: str
    task_code: str
    task_name: str
    project_reference: str
    project_name: str

    allocation_percent: int
    covered_working_days: int
    week_working_days: int

    workload_percent: Decimal


@dataclass(frozen=True)
class WorkloadCell:
    """
    Charge d'une ressource pour une semaine.

    status permet au rendu de distinguer :
    - empty     : aucune charge ;
    - available : charge inférieure à 100 % ;
    - nominal   : charge égale à 100 % ;
    - overload  : charge supérieure à 100 %.
    """

    week: WorkloadWeek
    workload_percent: Decimal
    status: str
    details: tuple[WorkloadTaskDetail, ...]


@dataclass(frozen=True)
class WorkloadResource:
    """
    Ligne du plan de charge pour une ressource.
    """

    user_id: str
    last_name: str
    first_name: str

    cells: tuple[WorkloadCell, ...]


@dataclass(frozen=True)
class WorkloadPlan:
    """
    Plan de charge hebdomadaire.
    """

    date_from: date
    date_to: date

    weeks: tuple[WorkloadWeek, ...]
    resources: tuple[WorkloadResource, ...]


class WeeklyWorkloadService:
    """
    Construit le plan de charge hebdomadaire par ressource.

    Règle de calcul :

        taux hebdomadaire
        =
        taux d'affectation
        ×
        jours ouvrés de la tâche dans la semaine
        /
        jours ouvrés de la semaine

    Les jours ouvrés sont actuellement du lundi au vendredi.
    """

    ZERO_PERCENT = Decimal("0.00")
    NOMINAL_PERCENT = Decimal("100.00")

    STATUS_EMPTY = "empty"
    STATUS_AVAILABLE = "available"
    STATUS_NOMINAL = "nominal"
    STATUS_OVERLOAD = "overload"

    def build(
        self,
        *,
        date_from: date,
        date_to: date,
        project=None,
        accessible_projects,
    ) -> WorkloadPlan:
        """
        Construit le plan de charge sur la période demandée.

        Si un projet est fourni, seules les affectations de ce projet
        sont prises en compte.
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

        assignments = self._get_assignments(
            date_from=date_from,
            date_to=date_to,
            project=project,
            accessible_projects=accessible_projects,
        )

        assignments_by_user: dict[
            str,
            list[TaskAssignment],
        ] = {}

        users_by_id: dict[str, User] = {}

        for assignment in assignments:
            user_id = str(assignment.user_id)

            assignments_by_user.setdefault(
                user_id,
                [],
            ).append(
                assignment
            )

            users_by_id[user_id] = assignment.user

        resources: list[WorkloadResource] = []

        sorted_users = sorted(
            users_by_id.values(),
            key=lambda user: (
                user.last_name or "",
                user.first_name or "",
            ),
        )

        for user in sorted_users:
            user_id = str(user.pk)

            user_assignments = (
                assignments_by_user.get(
                    user_id,
                    [],
                )
            )

            cells = tuple(
                self._build_cell(
                    week=week,
                    assignments=user_assignments,
                )
                for week in weeks
            )

            resources.append(
                WorkloadResource(
                    user_id=user_id,
                    last_name=user.last_name,
                    first_name=user.first_name,
                    cells=cells,
                )
            )

        return WorkloadPlan(
            date_from=date_from,
            date_to=date_to,
            weeks=weeks,
            resources=tuple(resources),
        )

    # ------------------------------------------------------------------
    # Semaines
    # ------------------------------------------------------------------

    def _build_weeks(
        self,
        *,
        date_from: date,
        date_to: date,
    ) -> tuple[WorkloadWeek, ...]:
        """
        Construit les semaines ISO intersectant la période.

        Une semaine commence le lundi et se termine le dimanche.
        """

        weeks: list[WorkloadWeek] = []

        current = (
            date_from
            - timedelta(
                days=date_from.weekday()
            )
        )

        while current <= date_to:
            week_end = (
                current
                + timedelta(days=6)
            )

            _iso_year, iso_week, _iso_day = (
                current.isocalendar()
            )

            weeks.append(
                WorkloadWeek(
                    start_date=current,
                    end_date=week_end,
                    label=f"S{iso_week:02d}",
                )
            )

            current += timedelta(days=7)

        return tuple(weeks)

    # ------------------------------------------------------------------
    # Affectations
    # ------------------------------------------------------------------

    @staticmethod
    def _get_assignments(
        *,
        date_from: date,
        date_to: date,
        project=None,
        accessible_projects,
    ):
        """
        Retourne les affectations actives dont la tâche intersecte
        la période du plan de charge.
        """

        queryset = (
            TaskAssignment.objects
            .filter(
                task__work_package__project__in=(
                    accessible_projects
                ),
                is_active=True,
                user__is_active=True,
                task__is_active=True,
                task__start_date__isnull=False,
                task__end_date__isnull=False,
                task__start_date__lte=date_to,
                task__end_date__gte=date_from,

            )
            .select_related(
                "user",
                "task",
                "task__work_package",
                "task__work_package__project",
            )
            .order_by(
                "user__last_name",
                "user__first_name",
                "task__start_date",
                "task__code",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                task__work_package__project=project,
            )

        return queryset

    # ------------------------------------------------------------------
    # Cellule ressource / semaine
    # ------------------------------------------------------------------

    def _build_cell(
        self,
        *,
        week: WorkloadWeek,
        assignments,
    ) -> WorkloadCell:
        """
        Calcule la charge d'une ressource sur une semaine.
        """

        details: list[WorkloadTaskDetail] = []

        workload_total = self.ZERO_PERCENT

        week_working_days = (
            self._count_working_days(
                start_date=week.start_date,
                end_date=week.end_date,
            )
        )

        if week_working_days == 0:
            return WorkloadCell(
                week=week,
                workload_percent=self.ZERO_PERCENT,
                status=self.STATUS_EMPTY,
                details=(),
            )

        for assignment in assignments:
            task = assignment.task

            if not self._intersects(
                start_date=task.start_date,
                end_date=task.end_date,
                period_start=week.start_date,
                period_end=week.end_date,
            ):
                continue

            visible_start = max(
                task.start_date,
                week.start_date,
            )

            visible_end = min(
                task.end_date,
                week.end_date,
            )

            covered_working_days = (
                self._count_working_days(
                    start_date=visible_start,
                    end_date=visible_end,
                )
            )

            if covered_working_days == 0:
                continue

            workload_percent = (
                Decimal(
                    assignment.allocation_percent
                )
                * Decimal(
                    covered_working_days
                )
                / Decimal(
                    week_working_days
                )
            )

            workload_percent = (
                workload_percent.quantize(
                    Decimal("0.01")
                )
            )

            workload_total += workload_percent

            project = (
                task
                .work_package
                .project
            )

            details.append(
                WorkloadTaskDetail(
                    task_id=str(task.pk),
                    task_code=task.code,
                    task_name=task.name,
                    project_reference=(
                        project.reference
                    ),
                    project_name=project.name,
                    allocation_percent=(
                        assignment.allocation_percent
                    ),
                    covered_working_days=(
                        covered_working_days
                    ),
                    week_working_days=(
                        week_working_days
                    ),
                    workload_percent=(
                        workload_percent
                    ),
                )
            )

        workload_total = (
            workload_total.quantize(
                Decimal("0.01")
            )
        )

        return WorkloadCell(
            week=week,
            workload_percent=workload_total,
            status=self._get_workload_status(
                workload_total
            ),
            details=tuple(details),
        )

    # ------------------------------------------------------------------
    # État de charge
    # ------------------------------------------------------------------

    def _get_workload_status(
        self,
        workload_percent: Decimal,
    ) -> str:
        """
        Détermine l'état visuel correspondant au taux de charge.
        """

        if workload_percent <= self.ZERO_PERCENT:
            return self.STATUS_EMPTY

        if workload_percent < self.NOMINAL_PERCENT:
            return self.STATUS_AVAILABLE

        if workload_percent == self.NOMINAL_PERCENT:
            return self.STATUS_NOMINAL

        return self.STATUS_OVERLOAD

    # ------------------------------------------------------------------
    # Jours ouvrés
    # ------------------------------------------------------------------

    @staticmethod
    def _count_working_days(
        *,
        start_date: date,
        end_date: date,
    ) -> int:
        """
        Compte les jours ouvrés entre deux dates incluses.

        Première version :
        lundi à vendredi uniquement.

        Les jours fériés ne sont pas encore déduits.
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

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

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