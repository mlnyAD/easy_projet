from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from django.db import transaction
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce

from apps.reporting.models import (
    ActivityReportEntry,
    ActivityReportProjectReviewStatus,
)


class TaskWorkloadService:
    """
    Consolide les heures validées des rapports d'activité.

    Le consommé reste calculé à partir des saisies validées. Les
    valeurs de pilotage de la tâche ne sont synchronisées que tant
    qu'elles n'ont pas été corrigées manuellement par le CP.
    """

    ZERO_HOURS = Decimal("0.00")

    HOURS_FIELD = DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    @classmethod
    def get_consumed_hours_by_task(
        cls,
        *,
        task_ids: Iterable,
        up_to_date: date | None = None,
    ) -> dict:
        """
        Retourne le consommé validé pour chaque tâche demandée.

        Une saisie est prise en compte seulement lorsqu'une revue du
        projet correspondant est validée.
        """

        normalized_task_ids = tuple(task_ids)

        if not normalized_task_ids:
            return {}

        filters = {
            "activity_report_line__is_active": True,
            "activity_report_line__task_id__in": (
                normalized_task_ids
            ),
            "activity_report_line__activity_report__is_active": True,
            (
                "activity_report_line__activity_report__"
                "project_reviews__status"
            ): ActivityReportProjectReviewStatus.VALIDATED,
            (
                "activity_report_line__activity_report__"
                "project_reviews__project_id"
            ): F(
                "activity_report_line__task__"
                "work_package__project_id"
            ),
        }

        if up_to_date is not None:
            filters["activity_date__lte"] = up_to_date

        queryset = (
            ActivityReportEntry.objects
            .filter(**filters)
            .values("activity_report_line__task_id")
            .annotate(
                regular_hours_total=Coalesce(
                    Sum("regular_hours"),
                    Value(cls.ZERO_HOURS),
                    output_field=cls.HOURS_FIELD,
                ),
                overtime_hours_total=Coalesce(
                    Sum("overtime_hours"),
                    Value(cls.ZERO_HOURS),
                    output_field=cls.HOURS_FIELD,
                ),
            )
        )

        return {
            row["activity_report_line__task_id"]: (
                row["regular_hours_total"]
                + row["overtime_hours_total"]
            )
            for row in queryset
        }

    @classmethod
    def synchronize_project(
        cls,
        *,
        project,
    ) -> None:
        """
        Synchronise le RAF et l'avancement automatique des tâches
        d'un projet après validation d'un rapport d'activité.
        """

        from apps.tasks.models import Task

        task_ids = tuple(
            Task.objects
            .filter(work_package__project=project)
            .values_list("pk", flat=True)
        )

        cls.synchronize_tasks(task_ids=task_ids)

    @classmethod
    def synchronize_tasks(
        cls,
        *,
        task_ids: Iterable,
    ) -> None:
        """
        Met à jour les indicateurs automatiques des tâches demandées.
        """

        from apps.tasks.models import Task

        normalized_task_ids = tuple(task_ids)

        if not normalized_task_ids:
            return

        consumed_hours_by_task = (
            cls.get_consumed_hours_by_task(
                task_ids=normalized_task_ids,
            )
        )

        with transaction.atomic():
            tasks = (
                Task.objects
                .select_for_update()
                .filter(pk__in=normalized_task_ids)
            )

            for task in tasks:
                consumed_hours = consumed_hours_by_task.get(
                    task.pk,
                    cls.ZERO_HOURS,
                )

                update_fields = []

                if not task.remaining_workload_hours_is_manual:
                    remaining_hours = cls.get_remaining_hours(
                        planned_hours=task.planned_workload_hours,
                        consumed_hours=consumed_hours,
                    )

                    if task.remaining_workload_hours != remaining_hours:
                        task.remaining_workload_hours = remaining_hours
                        update_fields.append(
                            "remaining_workload_hours"
                        )

                if not task.progress_percent_is_manual:
                    progress_percent = cls.get_progress_percent(
                        planned_hours=task.planned_workload_hours,
                        consumed_hours=consumed_hours,
                    )

                    if task.progress_percent != progress_percent:
                        task.progress_percent = progress_percent
                        update_fields.append("progress_percent")

                if update_fields:
                    update_fields.append("updated_at")
                    task.save(update_fields=update_fields)

    @classmethod
    def get_remaining_hours(
        cls,
        *,
        planned_hours: int,
        consumed_hours: Decimal,
    ) -> Decimal:
        return max(
            Decimal(planned_hours) - consumed_hours,
            cls.ZERO_HOURS,
        )

    @staticmethod
    def get_progress_percent(
        *,
        planned_hours: int,
        consumed_hours: Decimal,
    ) -> int:
        if planned_hours <= 0:
            return 0

        progress = (
            consumed_hours
            / Decimal(planned_hours)
            * Decimal("100")
        )

        return min(
            100,
            int(
                progress.to_integral_value(
                    rounding=ROUND_HALF_UP,
                )
            ),
        )
