


from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.work.models import WorkPackage


@dataclass(frozen=True)
class PlanningCalendarEvent:
    """
    Événement affichable dans le calendrier Planning.
    """

    event_type: str
    object_type: str
    object_id: str

    title: str
    subtitle: str

    event_date: date

    project_id: str
    project_reference: str
    project_name: str


@dataclass(frozen=True)
class PlanningCalendarDay:
    """
    Journée du calendrier mensuel.
    """

    day: date
    is_current_month: bool

    events: tuple[
        PlanningCalendarEvent,
        ...
    ]


@dataclass(frozen=True)
class PlanningCalendarWeek:
    """
    Semaine du calendrier mensuel.
    """

    days: tuple[
        PlanningCalendarDay,
        ...
    ]


@dataclass(frozen=True)
class PlanningCalendar:
    """
    Calendrier mensuel du module Planning.
    """

    year: int
    month: int

    month_label: str

    previous_year: int
    previous_month: int

    next_year: int
    next_month: int

    weeks: tuple[
        PlanningCalendarWeek,
        ...
    ]


class PlanningCalendarService:
    """
    Construit le calendrier mensuel du module Planning.

    Première version :
    - début projet ;
    - fin projet ;
    - réception projet ;
    - livraison projet ;
    - début lot ;
    - fin lot ;
    - début tâche ;
    - fin tâche.

    Le service ne contient aucune logique de rendu.
    """

    EVENT_PROJECT_START = "project_start"
    EVENT_PROJECT_END = "project_end"
    EVENT_PROJECT_RECEIPT = "project_receipt"
    EVENT_PROJECT_DELIVERY = "project_delivery"

    EVENT_WORK_PACKAGE_START = "work_package_start"
    EVENT_WORK_PACKAGE_END = "work_package_end"

    EVENT_TASK_START = "task_start"
    EVENT_TASK_END = "task_end"

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

    def build(
        self,
        *,
        year: int,
        month: int,
        project: Project | None = None,
        accessible_projects,
    ) -> PlanningCalendar:
        """
        Construit le calendrier pour le mois demandé.
        """

        self._validate_month(
            year=year,
            month=month,
        )

        month_start = date(
            year,
            month,
            1,
        )

        month_end = self._get_month_end(
            year=year,
            month=month,
        )

        calendar_start = self._get_calendar_start(
            month_start
        )

        calendar_end = self._get_calendar_end(
            month_end
        )

        events = self._get_events(
            date_from=calendar_start,
            date_to=calendar_end,
            project=project,
            accessible_projects=accessible_projects,
        )

        events_by_date: dict[
            date,
            list[PlanningCalendarEvent],
        ] = {}

        for event in events:
            events_by_date.setdefault(
                event.event_date,
                [],
            ).append(
                event
            )

        weeks = self._build_weeks(
            calendar_start=calendar_start,
            calendar_end=calendar_end,
            month=month,
            events_by_date=events_by_date,
        )

        (
            previous_year,
            previous_month,
        ) = self._get_previous_month(
            year=year,
            month=month,
        )

        (
            next_year,
            next_month,
        ) = self._get_next_month(
            year=year,
            month=month,
        )

        return PlanningCalendar(
            year=year,
            month=month,
            month_label=(
                f"{self.MONTH_NAMES[month]} {year}"
            ),
            previous_year=previous_year,
            previous_month=previous_month,
            next_year=next_year,
            next_month=next_month,
            weeks=weeks,
        )

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------

    def _get_events(
        self,
        *,
        date_from: date,
        date_to: date,
        project: Project | None,
        accessible_projects,
    ) -> tuple[
        PlanningCalendarEvent,
        ...
    ]:
        """
        Consolide tous les événements visibles dans la période.
        """

        events: list[
            PlanningCalendarEvent
        ] = []

        projects = self._get_projects(
            date_from=date_from,
            date_to=date_to,
            project=project,
            accessible_projects=accessible_projects,
        )

        project_ids = [
            current_project.pk
            for current_project in projects
        ]

        for current_project in projects:
            events.extend(
                self._build_project_events(
                    project=current_project,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

        if not project_ids:
            return tuple(events)

        work_packages = (
            WorkPackage.objects
            .filter(
                project_id__in=project_ids,
                is_active=True,
            )
            .select_related(
                "project",
            )
            .order_by(
                "project__reference",
                "code",
                "name",
            )
        )

        work_package_ids = []

        for work_package in work_packages:
            work_package_ids.append(
                work_package.pk
            )

            events.extend(
                self._build_work_package_events(
                    work_package=work_package,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

        if not work_package_ids:
            return tuple(
                self._sort_events(events)
            )

        tasks = (
            Task.objects
            .filter(
                work_package_id__in=(
                    work_package_ids
                ),
                is_active=True,
            )
            .select_related(
                "work_package",
                "work_package__project",
            )
            .order_by(
                "work_package__project__reference",
                "work_package__code",
                "code",
                "name",
            )
        )

        for task in tasks:
            events.extend(
                self._build_task_events(
                    task=task,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

        return tuple(
            self._sort_events(events)
        )

    def _get_projects(
        self,
        *,
        date_from: date,
        date_to: date,
        project: Project | None,
        accessible_projects,
    ) -> list[Project]:

        queryset = (
            accessible_projects
            .filter(is_active=True)
            .order_by(
                "reference",
                "name",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                pk=project.pk
            )

        result = []

        for current_project in queryset:
            project_dates = (
                current_project.start_date,
                current_project.end_date,
                current_project.receipt_date,
                current_project.delivery_date,
            )

            if any(
                self._date_in_period(
                    value=value,
                    date_from=date_from,
                    date_to=date_to,
                )
                for value in project_dates
            ):
                result.append(
                    current_project
                )
                continue

            if (
                WorkPackage.objects
                .filter(
                    project=current_project,
                    is_active=True,
                )
                .filter(
                    start_date__lte=date_to,
                    end_date__gte=date_from,
                )
                .exists()
            ):
                result.append(
                    current_project
                )
                continue

            if (
                Task.objects
                .filter(
                    work_package__project=(
                        current_project
                    ),
                    is_active=True,
                )
                .filter(
                    start_date__lte=date_to,
                    end_date__gte=date_from,
                )
                .exists()
            ):
                result.append(
                    current_project
                )

        return result

    # ------------------------------------------------------------------
    # Construction des événements
    # ------------------------------------------------------------------

    def _build_project_events(
        self,
        *,
        project: Project,
        date_from: date,
        date_to: date,
    ) -> list[
        PlanningCalendarEvent
    ]:
        events = []

        self._append_event(
            events=events,
            event_type=self.EVENT_PROJECT_START,
            object_type="project",
            object_id=str(project.pk),
            title=f"Début projet — {project.reference}",
            subtitle=project.name,
            event_date=project.start_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_PROJECT_END,
            object_type="project",
            object_id=str(project.pk),
            title=f"Fin projet — {project.reference}",
            subtitle=project.name,
            event_date=project.end_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_PROJECT_RECEIPT,
            object_type="project",
            object_id=str(project.pk),
            title=f"Réception — {project.reference}",
            subtitle=project.name,
            event_date=project.receipt_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_PROJECT_DELIVERY,
            object_type="project",
            object_id=str(project.pk),
            title=f"Livraison — {project.reference}",
            subtitle=project.name,
            event_date=project.delivery_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        return events

    def _build_work_package_events(
        self,
        *,
        work_package: WorkPackage,
        date_from: date,
        date_to: date,
    ) -> list[
        PlanningCalendarEvent
    ]:
        events = []

        project = work_package.project

        self._append_event(
            events=events,
            event_type=self.EVENT_WORK_PACKAGE_START,
            object_type="work_package",
            object_id=str(work_package.pk),
            title=f"Début lot — {work_package.code}",
            subtitle=work_package.name,
            event_date=work_package.start_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_WORK_PACKAGE_END,
            object_type="work_package",
            object_id=str(work_package.pk),
            title=f"Fin lot — {work_package.code}",
            subtitle=work_package.name,
            event_date=work_package.end_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        return events

    def _build_task_events(
        self,
        *,
        task: Task,
        date_from: date,
        date_to: date,
    ) -> list[
        PlanningCalendarEvent
    ]:
        events = []

        project = (
            task
            .work_package
            .project
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_TASK_START,
            object_type="task",
            object_id=str(task.pk),
            title=f"Début tâche — {task.code}",
            subtitle=task.name,
            event_date=task.start_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        self._append_event(
            events=events,
            event_type=self.EVENT_TASK_END,
            object_type="task",
            object_id=str(task.pk),
            title=f"Fin tâche — {task.code}",
            subtitle=task.name,
            event_date=task.end_date,
            project=project,
            date_from=date_from,
            date_to=date_to,
        )

        return events

    def _append_event(
        self,
        *,
        events: list[
            PlanningCalendarEvent
        ],
        event_type: str,
        object_type: str,
        object_id: str,
        title: str,
        subtitle: str,
        event_date: date | None,
        project: Project,
        date_from: date,
        date_to: date,
    ) -> None:
        """
        Ajoute un événement s'il possède une date visible.
        """

        if event_date is None:
            return

        if not self._date_in_period(
            value=event_date,
            date_from=date_from,
            date_to=date_to,
        ):
            return

        events.append(
            PlanningCalendarEvent(
                event_type=event_type,
                object_type=object_type,
                object_id=object_id,
                title=title,
                subtitle=subtitle,
                event_date=event_date,
                project_id=str(project.pk),
                project_reference=(
                    project.reference
                ),
                project_name=project.name,
            )
        )

    # ------------------------------------------------------------------
    # Construction du mois
    # ------------------------------------------------------------------

    def _build_weeks(
        self,
        *,
        calendar_start: date,
        calendar_end: date,
        month: int,
        events_by_date: dict[
            date,
            list[PlanningCalendarEvent],
        ],
    ) -> tuple[
        PlanningCalendarWeek,
        ...
    ]:
        weeks = []

        current = calendar_start

        while current <= calendar_end:
            days = []

            for _ in range(7):
                day_events = tuple(
                    events_by_date.get(
                        current,
                        [],
                    )
                )

                days.append(
                    PlanningCalendarDay(
                        day=current,
                        is_current_month=(
                            current.month
                            == month
                        ),
                        events=day_events,
                    )
                )

                current = (
                    current
                    .fromordinal(
                        current.toordinal() + 1
                    )
                )

            weeks.append(
                PlanningCalendarWeek(
                    days=tuple(days),
                )
            )

        return tuple(weeks)

    # ------------------------------------------------------------------
    # Dates du calendrier
    # ------------------------------------------------------------------

    @staticmethod
    def _get_calendar_start(
        month_start: date,
    ) -> date:
        """
        Retourne le lundi de la première semaine affichée.
        """

        return month_start.fromordinal(
            month_start.toordinal()
            - month_start.weekday()
        )

    @staticmethod
    def _get_calendar_end(
        month_end: date,
    ) -> date:
        """
        Retourne le dimanche de la dernière semaine affichée.
        """

        days_after = (
            6 - month_end.weekday()
        )

        return month_end.fromordinal(
            month_end.toordinal()
            + days_after
        )

    @staticmethod
    def _get_month_end(
        *,
        year: int,
        month: int,
    ) -> date:
        if month == 12:
            next_month = date(
                year + 1,
                1,
                1,
            )
        else:
            next_month = date(
                year,
                month + 1,
                1,
            )

        return next_month.fromordinal(
            next_month.toordinal() - 1
        )

    @staticmethod
    def _get_previous_month(
        *,
        year: int,
        month: int,
    ) -> tuple[int, int]:
        if month == 1:
            return (
                year - 1,
                12,
            )

        return (
            year,
            month - 1,
        )

    @staticmethod
    def _get_next_month(
        *,
        year: int,
        month: int,
    ) -> tuple[int, int]:
        if month == 12:
            return (
                year + 1,
                1,
            )

        return (
            year,
            month + 1,
        )

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_month(
        *,
        year: int,
        month: int,
    ) -> None:
        if year < 1:
            raise ValueError(
                "L'année doit être strictement positive."
            )

        if not 1 <= month <= 12:
            raise ValueError(
                "Le mois doit être compris entre 1 et 12."
            )

    @staticmethod
    def _date_in_period(
        *,
        value: date | None,
        date_from: date,
        date_to: date,
    ) -> bool:
        if value is None:
            return False

        return (
            date_from
            <= value
            <= date_to
        )

    @staticmethod
    def _sort_events(
        events: Iterable[
            PlanningCalendarEvent
        ],
    ) -> list[
        PlanningCalendarEvent
    ]:
        return sorted(
            events,
            key=lambda event: (
                event.event_date,
                event.project_reference,
                event.object_type,
                event.title,
            ),
        )