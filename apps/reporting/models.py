

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User
from common.models import TimeStampedModel


class ActivityReport(TimeStampedModel):
    """
    Rapport d'activité hebdomadaire d'un utilisateur.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="activity_reports",
        verbose_name="Utilisateur",
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="activity_report_statuses",
        verbose_name="Statut",
    )

    period_start_date = models.DateField(
        verbose_name="Début de période",
    )

    period_end_date = models.DateField(
        verbose_name="Fin de période",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Transmis le",
    )

    global_comment = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Commentaire",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Rapport actif",
    )

    class Meta:
        db_table = "activity_report"
        ordering = [
            "-period_start_date",
            "user__last_name",
            "user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "period_start_date",
                ],
                name="uniq_activity_report_user_week",
            ),
        ]
        verbose_name = "Rapport d'activité"
        verbose_name_plural = "Rapports d'activité"

    def clean(self) -> None:
        super().clean()

        if self.period_start_date.weekday() != 0:
            raise ValidationError(
                {
                    "period_start_date": (
                        "La période doit commencer un lundi."
                    ),
                }
            )

        expected_end_date = (
            self.period_start_date
            + timedelta(days=6)
        )

        if self.period_end_date != expected_end_date:
            raise ValidationError(
                {
                    "period_end_date": (
                        "La période doit se terminer le dimanche "
                        "suivant le début de période."
                    ),
                }
            )

        if (
            self.status_id
            and self.status.catalog_type.code
            != "ACTIVITY_REPORT"
        ):
            raise ValidationError(
                {
                    "status": (
                        "Le statut doit appartenir au catalogue "
                        "ACTIVITY_REPORT."
                    ),
                }
            )

    def __str__(self) -> str:
        return (
            f"{self.user} - "
            f"{self.period_start_date} / "
            f"{self.period_end_date}"
        )


class ActivityReportLine(TimeStampedModel):
    """
    Ligne d'un rapport d'activité.

    Une ligne correspond soit à une tâche, soit à une activité
    hors tâche.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    activity_report = models.ForeignKey(
        ActivityReport,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Rapport d'activité",
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.PROTECT,
        related_name="activity_report_lines",
        null=True,
        blank=True,
        verbose_name="Tâche",
    )

    line_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="activity_report_lines",
        null=True,
        blank=True,
        verbose_name="Type d'activité",
    )

    comment = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Commentaire",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ligne active",
    )

    class Meta:
        db_table = "activity_report_line"
        ordering = [
            "activity_report",
            "created_at",
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        task__isnull=False,
                        line_type__isnull=True,
                    )
                    | models.Q(
                        task__isnull=True,
                        line_type__isnull=False,
                    )
                ),
                name="chk_activity_report_line_source",
            ),
            models.UniqueConstraint(
                fields=[
                    "activity_report",
                    "task",
                ],
                condition=models.Q(
                    task__isnull=False,
                ),
                name="uniq_activity_report_task",
            ),
            models.UniqueConstraint(
                fields=[
                    "activity_report",
                    "line_type",
                ],
                condition=models.Q(
                    line_type__isnull=False,
                ),
                name="uniq_activity_report_line_type",
            ),
        ]
        verbose_name = "Ligne de rapport d'activité"
        verbose_name_plural = "Lignes de rapport d'activité"

    def clean(self) -> None:
        super().clean()

        if bool(self.task_id) == bool(self.line_type_id):
            raise ValidationError(
                "Une ligne doit être liée soit à une tâche, "
                "soit à un type d'activité hors tâche."
            )

        if (
            self.line_type_id
            and self.line_type.catalog_type.code
            != "ACTIVITY_REPORT_LINE"
        ):
            raise ValidationError(
                {
                    "line_type": (
                        "Le type doit appartenir au catalogue "
                        "ACTIVITY_REPORT_LINE."
                    ),
                }
            )

    def __str__(self) -> str:
        if self.task_id:
            return str(self.task)

        return self.line_type.label


class ActivityReportEntry(TimeStampedModel):
    """
    Saisie journalière d'une ligne de rapport d'activité.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    activity_report_line = models.ForeignKey(
        ActivityReportLine,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Ligne de rapport",
    )

    activity_date = models.DateField(
        verbose_name="Date",
    )

    regular_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Heures normales",
    )

    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Heures supplémentaires",
    )

    class Meta:
        db_table = "activity_report_entry"
        ordering = [
            "activity_report_line",
            "activity_date",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "activity_report_line",
                    "activity_date",
                ],
                name="uniq_activity_report_entry_day",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    regular_hours__gte=0,
                ),
                name="chk_activity_report_regular_hours",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    overtime_hours__gte=0,
                ),
                name="chk_activity_report_overtime_hours",
            ),
        ]
        verbose_name = "Saisie journalière du rapport d'activité"
        verbose_name_plural = (
            "Saisies journalières des rapports d'activité"
        )

    def clean(self) -> None:
        super().clean()

        report = self.activity_report_line.activity_report

        if not (
            report.period_start_date
            <= self.activity_date
            <= report.period_end_date
        ):
            raise ValidationError(
                {
                    "activity_date": (
                        "La date doit appartenir à la période "
                        "du rapport d'activité."
                    ),
                }
            )

    @property
    def total_hours(self):
        return (
            self.regular_hours
            + self.overtime_hours
        )

    def __str__(self) -> str:
        return (
            f"{self.activity_report_line} - "
            f"{self.activity_date}"
        )


class ActivityReportProjectReviewStatus(models.TextChoices):
    """
    État de validation d'une partie projet
    d'un rapport d'activité.
    """

    PENDING = (
        "PENDING",
        "À valider",
    )

    VALIDATED = (
        "VALIDATED",
        "Validé",
    )


class ActivityReportProjectReview(TimeStampedModel):
    """
    Validation d'un rapport d'activité pour un projet donné.

    Un rapport hebdomadaire peut concerner plusieurs projets.
    Chaque projet est validé indépendamment par la personne
    autorisée à traiter l'activité de ce projet.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    activity_report = models.ForeignKey(
        ActivityReport,
        on_delete=models.CASCADE,
        related_name="project_reviews",
        verbose_name="Rapport d'activité",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="activity_report_reviews",
        verbose_name="Projet",
    )

    status = models.CharField(
        max_length=20,
        choices=ActivityReportProjectReviewStatus.choices,
        default=ActivityReportProjectReviewStatus.PENDING,
        verbose_name="État",
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="activity_report_reviews",
        null=True,
        blank=True,
        verbose_name="Validé par",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Validé le",
    )

    class Meta:
        db_table = "activity_report_project_review"
        ordering = [
            "-activity_report__period_start_date",
            "project__reference",
            "activity_report__user__last_name",
            "activity_report__user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "activity_report",
                    "project",
                ],
                name="uniq_activity_report_project_review",
            ),
        ]
        permissions = [
            (
                "review_activity_reports",
                "Peut consulter et valider les rapports d'activité",
            ),
        ]
        verbose_name = "Validation de rapport d'activité par projet"
        verbose_name_plural = (
            "Validations de rapports d'activité par projet"
        )