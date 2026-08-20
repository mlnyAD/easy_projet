

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from apps.tasks.models import TaskAssignment


@dataclass(frozen=True)
class ResourceScheduleAssignment:
    """
    Affectation d'une ressource positionnée sur l'axe temporel.
    """

    assignment_id: str

    task_id: str
    task_code: str
    task_name: str

    work_package_code: str
    work_package_name: str

    project_id: str
    project_reference: str
    project_name: str

    start_date: date
    end_date: date

    allocation_percent: int

    left_percent: Decimal
    width_percent: Decimal


@dataclass(frozen=True)
class ResourceScheduleResource:
    """
    Ressource et ses affectations sur la période.
    """

    user_id: str
    last_name: str
    first_name: str
    email: str

    assignments: tuple[
        ResourceScheduleAssignment,
        ...,
    ]


@dataclass(frozen=True)
class ResourceSchedule:
    """
    Planning des ressources sur une période.
    """

    date_from: date
    date_to: date

    resources: tuple[
        ResourceScheduleResource,
        ...,
    ]


class ResourceScheduleService:
    """
    Construit le planning ressources.

    Le service répond à la question :

        Qui fait quoi, quand ?

    Seules sont retenues les affectations :
    - actives ;
    - portant sur un utilisateur actif ;
    - portant sur une tâche active ;
    - disposant de dates courantes exploitables ;
    - intersectant la période demandée.
    """

    PERCENT_QUANTIZER = Decimal("0.0001")

    def build(
        self,
        *,
        date_from: date,
        date_to: date,
        project=None,
    ) -> ResourceSchedule:
        """
        Construit le planning ressources sur la période.
        """

        if date_to < date_from:
            raise ValueError(
                "La date de fin ne peut pas être antérieure "
                "à la date de début."
            )

        assignments = self._get_assignments(
            date_from=date_from,
            date_to=date_to,
            project=project,
        )

        assignments_by_user = {}

        for assignment in assignments:
            user_id = str(assignment.user_id)

            if user_id not in assignments_by_user:
                assignments_by_user[user_id] = {
                    "user": assignment.user,
                    "assignments": [],
                }

            schedule_assignment = (
                self._build_assignment(
                    assignment=assignment,
                    date_from=date_from,
                    date_to=date_to,
                )
            )

            assignments_by_user[
                user_id
            ]["assignments"].append(
                schedule_assignment
            )

        resources = []

        for resource_data in assignments_by_user.values():
            user = resource_data["user"]

            resource_assignments = sorted(
                resource_data["assignments"],
                key=lambda item: (
                    item.start_date,
                    item.end_date,
                    item.project_reference,
                    item.task_code,
                ),
            )

            resources.append(
                ResourceScheduleResource(
                    user_id=str(user.pk),
                    last_name=user.last_name,
                    first_name=user.first_name,
                    email=user.email,
                    assignments=tuple(
                        resource_assignments
                    ),
                )
            )

        resources.sort(
            key=lambda resource: (
                resource.last_name or "",
                resource.first_name or "",
            )
        )

        return ResourceSchedule(
            date_from=date_from,
            date_to=date_to,
            resources=tuple(resources),
        )

    # ------------------------------------------------------------------
    # Affectations
    # ------------------------------------------------------------------

    @staticmethod
    def _get_assignments(
        *,
        date_from: date,
        date_to: date,
        project=None,
    ):
        """
        Retourne les affectations pertinentes pour la période.
        """

        queryset = (
            TaskAssignment.objects
            .filter(
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
                "task__end_date",
                "task__code",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                task__work_package__project=project,
            )

        return queryset

    # ------------------------------------------------------------------
    # Construction d'une affectation
    # ------------------------------------------------------------------

    def _build_assignment(
        self,
        *,
        assignment: TaskAssignment,
        date_from: date,
        date_to: date,
    ) -> ResourceScheduleAssignment:
        """
        Construit une affectation et sa position graphique.

        Le calcul de positionnement reprend exactement la convention
        utilisée par le Gantt principal.
        """

        task = assignment.task
        work_package = task.work_package
        project = work_package.project

        (
            left_percent,
            width_percent,
        ) = self._get_schedule_position(
            start_date=task.start_date,
            end_date=task.end_date,
            date_from=date_from,
            date_to=date_to,
        )

        return ResourceScheduleAssignment(
            assignment_id=str(assignment.pk),
            task_id=str(task.pk),
            task_code=task.code,
            task_name=task.name,
            work_package_code=work_package.code,
            work_package_name=work_package.name,
            project_id=str(project.pk),
            project_reference=project.reference,
            project_name=project.name,
            start_date=task.start_date,
            end_date=task.end_date,
            allocation_percent=(
                assignment.allocation_percent
            ),
            left_percent=Decimal(
                str(left_percent)
            ),
            width_percent=Decimal(
                str(width_percent)
            ),
        )

    # ------------------------------------------------------------------
    # Positionnement temporel
    # ------------------------------------------------------------------

    @staticmethod
    def _get_schedule_position(
        *,
        start_date: date,
        end_date: date,
        date_from: date,
        date_to: date,
    ) -> tuple[float, float]:
        """
        Calcule la position d'une affectation dans l'axe temporel.

        Convention identique au Gantt principal :
        - bornes inclusives ;
        - troncature aux limites visibles ;
        - position et largeur exprimées en pourcentage.
        """

        visible_start = max(
            start_date,
            date_from,
        )

        visible_end = min(
            end_date,
            date_to,
        )

        if visible_end < visible_start:
            return (
                0.0,
                0.0,
            )

        duration_days = (
            date_to - date_from
        ).days + 1

        start_offset = (
            visible_start - date_from
        ).days

        visible_duration_days = (
            visible_end - visible_start
        ).days + 1

        left_percent = (
            start_offset
            / duration_days
            * 100
        )

        width_percent = (
            visible_duration_days
            / duration_days
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