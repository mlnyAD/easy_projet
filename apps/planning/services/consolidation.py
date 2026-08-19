

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable

from django.db.models import (
    DecimalField,
    F,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce

from apps.projects.models import Project
from apps.reporting.models import (
    ActivityReportEntry,
    ActivityReportProjectReviewStatus,
)
from apps.tasks.models import Task
from apps.work.models import WorkPackage


@dataclass(frozen=True)
class PlanningPeriod:
    """
    Période affichée par le planning.
    """

    date_from: date
    date_to: date
    state_date: date

    def __post_init__(self) -> None:
        if self.date_to < self.date_from:
            raise ValueError(
                "La date de fin de période ne peut pas être "
                "antérieure à la date de début."
            )

    @property
    def duration_days(self) -> int:
        """
        Nombre de jours calendaires affichés.

        Les deux bornes sont incluses.
        """
        return (
            self.date_to - self.date_from
        ).days + 1


@dataclass(frozen=True)
class PlanningCalendarSegment:
    """
    Segment d'en-tête du calendrier du Gantt.
    """

    label: str

    date_from: date
    date_to: date

    left_percent: float
    width_percent: float


@dataclass(frozen=True)
class PlanningItem:
    """
    Élément présenté dans le planning.
    """

    object_type: str
    object_id: str

    code: str
    name: str

    level: int

    initial_start_date: date | None
    initial_end_date: date | None

    start_date: date | None
    end_date: date | None

    planned_workload_hours: int

    actual_hours: Decimal = Decimal("0.00")

    parent_id: str | None = None

    # ------------------------------------------------------------------
    # Positionnement global de la barre Gantt
    # ------------------------------------------------------------------

    gantt_left_percent: float | None = None
    gantt_width_percent: float | None = None

    # ------------------------------------------------------------------
    # Répartition de la barre par rapport à la date de situation
    #
    # Ces pourcentages sont relatifs à la largeur de la barre,
    # et non à la largeur totale du planning.
    # ------------------------------------------------------------------

    realized_width_percent: float = 0.0
    forecast_width_percent: float = 100.0


@dataclass(frozen=True)
class PlanningData:
    """
    Données consolidées nécessaires aux représentations du planning.
    """

    period: PlanningPeriod

    items: tuple[
        PlanningItem,
        ...
    ]

    months: tuple[
        PlanningCalendarSegment,
        ...
    ]

    weeks: tuple[
        PlanningCalendarSegment,
        ...
    ]

    state_date_percent: float | None


class PlanningConsolidationService:
    """
    Construit les données communes aux différentes représentations
    du planning.

    Principes :
    - les dates initiales constituent la référence ;
    - les dates courantes constituent le planning actif ;
    - la date de situation sépare la partie passée de la partie
      prévisionnelle ;
    - les heures réalisées proviennent uniquement des rapports
      d'activité validés pour le projet concerné ;
    - aucune donnée métier n'est modifiée par ce service.
    """

    PROJECT_LEVEL = 0
    WORK_PACKAGE_LEVEL = 1
    TASK_LEVEL = 2

    ZERO_HOURS = Decimal("0.00")

    HOURS_FIELD = DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    MONTH_NAMES = (
        "",
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre",
    )

    # ------------------------------------------------------------------
    # Construction générale
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        period: PlanningPeriod,
        project: Project | None = None,
    ) -> PlanningData:
        """
        Construit les données du planning pour la période demandée.
        """

        projects = list(
            self._get_projects(
                period=period,
                project=project,
            )
        )

        structure = []

        task_ids = []

        # --------------------------------------------------------------
        # Première passe :
        # construction de la hiérarchie visible
        # --------------------------------------------------------------

        for current_project in projects:

            work_packages = list(
                self._get_work_packages(
                    project=current_project,
                    period=period,
                )
            )

            package_structure = []

            for work_package in work_packages:

                tasks = list(
                    self._get_tasks(
                        work_package=work_package,
                        period=period,
                    )
                )

                task_ids.extend(
                    task.pk
                    for task in tasks
                )

                package_structure.append(
                    (
                        work_package,
                        tasks,
                    )
                )

            structure.append(
                (
                    current_project,
                    package_structure,
                )
            )

        # --------------------------------------------------------------
        # Heures réalisées validées
        # --------------------------------------------------------------

        actual_hours_by_task = (
            self._get_actual_hours_by_task(
                task_ids=task_ids,
                state_date=period.state_date,
            )
        )

        # --------------------------------------------------------------
        # Deuxième passe :
        # création des PlanningItem
        # --------------------------------------------------------------

        items: list[PlanningItem] = []

        for (
            current_project,
            package_structure,
        ) in structure:

            project_actual_hours = (
                self.ZERO_HOURS
            )

            project_items = []

            for (
                work_package,
                tasks,
            ) in package_structure:

                work_package_actual_hours = (
                    self.ZERO_HOURS
                )

                task_items = []

                for task in tasks:

                    actual_hours = (
                        actual_hours_by_task.get(
                            task.pk,
                            self.ZERO_HOURS,
                        )
                    )

                    work_package_actual_hours += (
                        actual_hours
                    )

                    task_items.append(
                        self._build_task_item(
                            task,
                            period=period,
                            actual_hours=actual_hours,
                        )
                    )

                project_actual_hours += (
                    work_package_actual_hours
                )

                project_items.append(
                    (
                        self._build_work_package_item(
                            work_package,
                            period=period,
                            actual_hours=(
                                work_package_actual_hours
                            ),
                        ),
                        task_items,
                    )
                )

            items.append(
                self._build_project_item(
                    current_project,
                    period=period,
                    actual_hours=project_actual_hours,
                )
            )

            for (
                work_package_item,
                task_items,
            ) in project_items:

                items.append(
                    work_package_item
                )

                items.extend(
                    task_items
                )

        return PlanningData(
            period=period,
            items=tuple(items),
            months=self._build_month_segments(
                period
            ),
            weeks=self._build_week_segments(
                period
            ),
            state_date_percent=(
                self._get_state_date_percent(
                    period
                )
            ),
        )

    # ------------------------------------------------------------------
    # Sélection
    # ------------------------------------------------------------------

    def _get_projects(
        self,
        *,
        period: PlanningPeriod,
        project: Project | None,
    ) -> Iterable[Project]:

        queryset = (
            Project.objects
            .filter(
                is_active=True
            )
            .select_related(
                "status",
                "project_manager",
            )
            .order_by(
                "reference",
                "name",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                pk=project.pk
            )

        return [
            current_project
            for current_project in queryset
            if self._intersects_period(
                start_date=(
                    current_project.start_date
                ),
                end_date=(
                    current_project.end_date
                ),
                period=period,
            )
        ]

    def _get_work_packages(
        self,
        *,
        project: Project,
        period: PlanningPeriod,
    ) -> Iterable[WorkPackage]:

        queryset = (
            WorkPackage.objects
            .filter(
                project=project,
                is_active=True,
            )
            .select_related(
                "status",
                "manager",
            )
            .order_by(
                "code",
                "name",
            )
        )

        return [
            work_package
            for work_package in queryset
            if self._intersects_period(
                start_date=(
                    work_package.start_date
                ),
                end_date=(
                    work_package.end_date
                ),
                period=period,
            )
        ]

    def _get_tasks(
        self,
        *,
        work_package: WorkPackage,
        period: PlanningPeriod,
    ) -> Iterable[Task]:

        queryset = (
            Task.objects
            .filter(
                work_package=work_package,
                is_active=True,
            )
            .select_related(
                "status"
            )
            .order_by(
                "code",
                "name",
            )
        )

        return [
            task
            for task in queryset
            if self._intersects_period(
                start_date=task.start_date,
                end_date=task.end_date,
                period=period,
            )
        ]

    # ------------------------------------------------------------------
    # Réalisé issu des rapports d'activité
    # ------------------------------------------------------------------

    def _get_actual_hours_by_task(
        self,
        *,
        task_ids,
        state_date: date,
    ) -> dict:
        """
        Retourne les heures réalisées validées par tâche.

        Une saisie est consolidée uniquement si :
        - elle appartient à une ligne active liée à une tâche ;
        - son rapport est actif ;
        - sa date est <= à la date de situation ;
        - une validation existe pour le projet de la tâche ;
        - cette validation possède l'état VALIDATED.
        """

        if not task_ids:
            return {}

        queryset = (
            ActivityReportEntry.objects
            .filter(
                activity_report_line__is_active=True,
                activity_report_line__task_id__in=(
                    task_ids
                ),
                activity_report_line__activity_report__is_active=True,
                activity_date__lte=state_date,
            )
            .filter(
                **{
                    (
                        "activity_report_line__activity_report__"
                        "project_reviews__status"
                    ): (
                        ActivityReportProjectReviewStatus
                        .VALIDATED
                    ),
                    (
                        "activity_report_line__activity_report__"
                        "project_reviews__project_id"
                    ): F(
                        "activity_report_line__task__"
                        "work_package__project_id"
                    ),
                }
            )
            .values(
                "activity_report_line__task_id"
            )
            .annotate(
                regular_hours_total=Coalesce(
                    Sum(
                        "regular_hours"
                    ),
                    Value(
                        self.ZERO_HOURS
                    ),
                    output_field=(
                        self.HOURS_FIELD
                    ),
                ),
                overtime_hours_total=Coalesce(
                    Sum(
                        "overtime_hours"
                    ),
                    Value(
                        self.ZERO_HOURS
                    ),
                    output_field=(
                        self.HOURS_FIELD
                    ),
                ),
            )
        )

        result = {}

        for row in queryset:

            task_id = row[
                "activity_report_line__task_id"
            ]

            result[task_id] = (
                row["regular_hours_total"]
                + row["overtime_hours_total"]
            )

        return result

    # ------------------------------------------------------------------
    # Construction des éléments
    # ------------------------------------------------------------------

    def _build_project_item(
        self,
        project: Project,
        *,
        period: PlanningPeriod,
        actual_hours: Decimal,
    ) -> PlanningItem:

        (
            left,
            width,
        ) = self._get_gantt_position(
            start_date=project.start_date,
            end_date=project.end_date,
            period=period,
        )

        (
            realized_width,
            forecast_width,
        ) = self._get_state_distribution(
            start_date=project.start_date,
            end_date=project.end_date,
            state_date=period.state_date,
        )

        return PlanningItem(
            object_type="project",
            object_id=str(
                project.pk
            ),
            code=project.reference,
            name=project.name,
            level=self.PROJECT_LEVEL,
            initial_start_date=(
                project.initial_start_date
            ),
            initial_end_date=(
                project.initial_end_date
            ),
            start_date=project.start_date,
            end_date=project.end_date,
            planned_workload_hours=(
                project.planned_workload_hours
            ),
            actual_hours=actual_hours,
            gantt_left_percent=left,
            gantt_width_percent=width,
            realized_width_percent=(
                realized_width
            ),
            forecast_width_percent=(
                forecast_width
            ),
        )

    def _build_work_package_item(
        self,
        work_package: WorkPackage,
        *,
        period: PlanningPeriod,
        actual_hours: Decimal,
    ) -> PlanningItem:

        (
            left,
            width,
        ) = self._get_gantt_position(
            start_date=(
                work_package.start_date
            ),
            end_date=(
                work_package.end_date
            ),
            period=period,
        )

        (
            realized_width,
            forecast_width,
        ) = self._get_state_distribution(
            start_date=(
                work_package.start_date
            ),
            end_date=(
                work_package.end_date
            ),
            state_date=period.state_date,
        )

        return PlanningItem(
            object_type="work_package",
            object_id=str(
                work_package.pk
            ),
            parent_id=str(
                work_package.project_id
            ),
            code=work_package.code,
            name=work_package.name,
            level=self.WORK_PACKAGE_LEVEL,
            initial_start_date=(
                work_package.initial_start_date
            ),
            initial_end_date=(
                work_package.initial_end_date
            ),
            start_date=(
                work_package.start_date
            ),
            end_date=(
                work_package.end_date
            ),
            planned_workload_hours=(
                work_package.planned_workload_hours
            ),
            actual_hours=actual_hours,
            gantt_left_percent=left,
            gantt_width_percent=width,
            realized_width_percent=(
                realized_width
            ),
            forecast_width_percent=(
                forecast_width
            ),
        )

    def _build_task_item(
        self,
        task: Task,
        *,
        period: PlanningPeriod,
        actual_hours: Decimal,
    ) -> PlanningItem:

        (
            left,
            width,
        ) = self._get_gantt_position(
            start_date=task.start_date,
            end_date=task.end_date,
            period=period,
        )

        (
            realized_width,
            forecast_width,
        ) = self._get_state_distribution(
            start_date=task.start_date,
            end_date=task.end_date,
            state_date=period.state_date,
        )

        return PlanningItem(
            object_type="task",
            object_id=str(
                task.pk
            ),
            parent_id=str(
                task.work_package_id
            ),
            code=task.code,
            name=task.name,
            level=self.TASK_LEVEL,
            initial_start_date=(
                task.initial_start_date
            ),
            initial_end_date=(
                task.initial_end_date
            ),
            start_date=task.start_date,
            end_date=task.end_date,
            planned_workload_hours=(
                task.planned_workload_hours
            ),
            actual_hours=actual_hours,
            gantt_left_percent=left,
            gantt_width_percent=width,
            realized_width_percent=(
                realized_width
            ),
            forecast_width_percent=(
                forecast_width
            ),
        )

    # ------------------------------------------------------------------
    # Répartition autour de la date de situation
    # ------------------------------------------------------------------

    @staticmethod
    def _get_state_distribution(
        *,
        start_date: date | None,
        end_date: date | None,
        state_date: date,
    ) -> tuple[
        float,
        float,
    ]:
        """
        Calcule la répartition d'une barre autour de la date
        de situation.

        Les pourcentages retournés sont relatifs à la barre :

            réalisé + prévisionnel = 100 %

        Une journée située exactement à la date de situation
        appartient à la partie réalisée.
        """

        if (
            start_date is None
            and end_date is None
        ):
            return (
                0.0,
                100.0,
            )

        effective_start = (
            start_date
            or end_date
        )

        effective_end = (
            end_date
            or start_date
        )

        if (
            effective_start is None
            or effective_end is None
        ):
            return (
                0.0,
                100.0,
            )

        # ----------------------------------------------------------
        # Barre entièrement après la date de situation
        # ----------------------------------------------------------

        if effective_start > state_date:
            return (
                0.0,
                100.0,
            )

        # ----------------------------------------------------------
        # Barre entièrement avant ou à la date de situation
        # ----------------------------------------------------------

        if effective_end <= state_date:
            return (
                100.0,
                0.0,
            )

        # ----------------------------------------------------------
        # La date de situation traverse la barre
        # ----------------------------------------------------------

        total_days = (
            effective_end
            - effective_start
        ).days + 1

        realized_days = (
            state_date
            - effective_start
        ).days + 1

        realized_percent = (
            realized_days
            / total_days
            * 100
        )

        realized_percent = round(
            realized_percent,
            6,
        )

        forecast_percent = round(
            100.0
            - realized_percent,
            6,
        )

        return (
            realized_percent,
            forecast_percent,
        )

    # ------------------------------------------------------------------
    # Calendrier
    # ------------------------------------------------------------------

    def _build_month_segments(
        self,
        period: PlanningPeriod,
    ) -> tuple[
        PlanningCalendarSegment,
        ...
    ]:

        segments = []

        current = date(
            period.date_from.year,
            period.date_from.month,
            1,
        )

        while current <= period.date_to:

            next_month = (
                self._first_day_of_next_month(
                    current
                )
            )

            month_end = (
                next_month
                - timedelta(days=1)
            )

            visible_start = max(
                current,
                period.date_from,
            )

            visible_end = min(
                month_end,
                period.date_to,
            )

            if visible_start <= visible_end:

                (
                    left,
                    width,
                ) = self._get_segment_position(
                    date_from=visible_start,
                    date_to=visible_end,
                    period=period,
                )

                segments.append(
                    PlanningCalendarSegment(
                        label=(
                            f"{self.MONTH_NAMES[current.month]} "
                            f"{current.year}"
                        ),
                        date_from=visible_start,
                        date_to=visible_end,
                        left_percent=left,
                        width_percent=width,
                    )
                )

            current = next_month

        return tuple(
            segments
        )

    def _build_week_segments(
        self,
        period: PlanningPeriod,
    ) -> tuple[
        PlanningCalendarSegment,
        ...
    ]:

        segments = []

        current = (
            period.date_from
            - timedelta(
                days=(
                    period.date_from.weekday()
                )
            )
        )

        while current <= period.date_to:

            week_end = (
                current
                + timedelta(days=6)
            )

            visible_start = max(
                current,
                period.date_from,
            )

            visible_end = min(
                week_end,
                period.date_to,
            )

            if visible_start <= visible_end:

                (
                    _iso_year,
                    iso_week,
                    _iso_day,
                ) = current.isocalendar()

                (
                    left,
                    width,
                ) = self._get_segment_position(
                    date_from=visible_start,
                    date_to=visible_end,
                    period=period,
                )

                segments.append(
                    PlanningCalendarSegment(
                        label=(
                            f"S{iso_week:02d}"
                        ),
                        date_from=visible_start,
                        date_to=visible_end,
                        left_percent=left,
                        width_percent=width,
                    )
                )

            current += timedelta(
                days=7
            )

        return tuple(
            segments
        )

    @staticmethod
    def _first_day_of_next_month(
        value: date,
    ) -> date:

        if value.month == 12:
            return date(
                value.year + 1,
                1,
                1,
            )

        return date(
            value.year,
            value.month + 1,
            1,
        )

    # ------------------------------------------------------------------
    # Positionnement Gantt
    # ------------------------------------------------------------------

    @staticmethod
    def _get_gantt_position(
        *,
        start_date: date | None,
        end_date: date | None,
        period: PlanningPeriod,
    ) -> tuple[
        float | None,
        float | None,
    ]:

        if (
            start_date is None
            and end_date is None
        ):
            return (
                None,
                None,
            )

        effective_start = (
            start_date
            or end_date
        )

        effective_end = (
            end_date
            or start_date
        )

        if (
            effective_start is None
            or effective_end is None
        ):
            return (
                None,
                None,
            )

        visible_start = max(
            effective_start,
            period.date_from,
        )

        visible_end = min(
            effective_end,
            period.date_to,
        )

        if visible_end < visible_start:
            return (
                None,
                None,
            )

        return (
            PlanningConsolidationService
            ._get_segment_position(
                date_from=visible_start,
                date_to=visible_end,
                period=period,
            )
        )

    @staticmethod
    def _get_segment_position(
        *,
        date_from: date,
        date_to: date,
        period: PlanningPeriod,
    ) -> tuple[
        float,
        float,
    ]:

        start_offset = (
            date_from
            - period.date_from
        ).days

        duration_days = (
            date_to
            - date_from
        ).days + 1

        left_percent = (
            start_offset
            / period.duration_days
            * 100
        )

        width_percent = (
            duration_days
            / period.duration_days
            * 100
        )

        return (
            round(
                left_percent,
                6,
            ),
            round(
                width_percent,
                6,
            ),
        )

    @staticmethod
    def _get_state_date_percent(
        period: PlanningPeriod,
    ) -> float | None:

        if not (
            period.date_from
            <= period.state_date
            <= period.date_to
        ):
            return None

        offset = (
            period.state_date
            - period.date_from
        ).days

        percent = (
            offset
            / period.duration_days
            * 100
        )

        return round(
            percent,
            6,
        )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def _intersects_period(
        *,
        start_date: date | None,
        end_date: date | None,
        period: PlanningPeriod,
    ) -> bool:

        if (
            start_date is None
            and end_date is None
        ):
            return False

        effective_start = (
            start_date
            or end_date
        )

        effective_end = (
            end_date
            or start_date
        )

        if (
            effective_start is None
            or effective_end is None
        ):
            return False

        return (
            effective_start
            <= period.date_to
            and effective_end
            >= period.date_from
        )