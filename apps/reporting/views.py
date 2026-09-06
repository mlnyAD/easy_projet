

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.db.models import (
    DecimalField,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
)
from apps.catalogs.models import CatalogValue
from apps.reporting.forms import (
    ActivityReportEntryFormSet,
)
from apps.reporting.models import (
    ActivityReportEntry,
    ActivityReportProjectReview,
    ActivityReportProjectReviewStatus,
)
from apps.reporting.services import (
    ActivityReportPreparationService,
)
from apps.reporting.permissions import (
    can_review_activity_reports,
)
from apps.projects.services.access import ProjectAccessService


# ======================================================================
# Rapport d'activité utilisateur
# ======================================================================

class ActivityReportView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Saisie du rapport d'activité hebdomadaire
    de l'utilisateur connecté.
    """

    template_name = (
        "reporting/activity_report.html"
    )

    ENTRY_PREFIX = "entries"

    # ------------------------------------------------------------------
    # Période
    # ------------------------------------------------------------------

    def get_week_start(self) -> date:
        """
        Retourne le lundi de la semaine demandée.

        Sans paramètre, utilise la semaine courante.

        Si une date quelconque est passée dans ?week=,
        elle est automatiquement ramenée au lundi
        correspondant.
        """

        value = self.request.GET.get("week")

        if value:
            try:
                selected_date = date.fromisoformat(
                    value
                )
            except ValueError as exc:
                raise Http404(
                    "La période demandée est invalide."
                ) from exc

        else:
            selected_date = timezone.localdate()

        return (
            selected_date
            - timedelta(
                days=selected_date.weekday()
            )
        )

    # ------------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------------

    def get_report(self):
        """
        Crée ou synchronise le rapport hebdomadaire
        de l'utilisateur connecté.
        """

        if not hasattr(self, "_report"):

            self._report = (
                ActivityReportPreparationService
                .prepare(
                    user=self.request.user,
                    period_start_date=(
                        self.get_week_start()
                    ),
                )
            )

        return self._report

    # ------------------------------------------------------------------
    # Entrées
    # ------------------------------------------------------------------

    def get_entries_queryset(self):
        """
        Limite strictement les saisies aux entrées
        appartenant au rapport courant.
        """

        report = self.get_report()

        return (
            ActivityReportEntry.objects
            .filter(
                activity_report_line__activity_report=(
                    report
                ),
                activity_report_line__is_active=True,
            )
            .select_related(
                "activity_report_line",
                "activity_report_line__task",
                (
                    "activity_report_line__task__"
                    "work_package"
                ),
                (
                    "activity_report_line__task__"
                    "work_package__project"
                ),
                "activity_report_line__line_type",
            )
            .order_by(
                "activity_report_line__created_at",
                "activity_date",
            )
        )

    def get_entry_formset(
        self,
        *,
        data=None,
    ):
        """
        Construit le formset des saisies journalières.
        """

        return ActivityReportEntryFormSet(
            data=data,
            queryset=self.get_entries_queryset(),
            prefix=self.ENTRY_PREFIX,
        )

    # ------------------------------------------------------------------
    # Présentation
    # ------------------------------------------------------------------

    def build_report_rows(
        self,
        formset,
    ):
        """
        Regroupe les 7 formulaires journaliers
        par ligne de rapport.
        """

        rows_by_line = {}

        for form in formset.forms:

            entry = form.instance
            line = entry.activity_report_line

            if line.pk not in rows_by_line:

                if line.task_id:

                    task = line.task

                    project = (
                        task
                        .work_package
                        .project
                    )

                    label = (
                        f"{task.code} - "
                        f"{task.name}"
                    )

                    project_label = (
                        f"{project.reference} - "
                        f"{project.name}"
                    )

                    line_kind = "task"

                else:

                    label = line.line_type.label
                    project_label = ""
                    line_kind = "activity"

                rows_by_line[line.pk] = {
                    "line": line,
                    "kind": line_kind,
                    "label": label,
                    "project_label": (
                        project_label
                    ),
                    "forms": [],
                }

            rows_by_line[
                line.pk
            ]["forms"].append(form)

        return list(
            rows_by_line.values()
        )

    # ------------------------------------------------------------------
    # Contexte
    # ------------------------------------------------------------------

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        report = self.get_report()

        formset = kwargs.get(
            "entry_formset"
        )

        if formset is None:
            formset = self.get_entry_formset()

        week_start = (
            report.period_start_date
        )

        week_end = (
            report.period_end_date
        )

        context.update(
            {
                "report": report,
                "entry_formset": formset,
                "report_rows": (
                    self.build_report_rows(
                        formset
                    )
                ),
                "week_start": week_start,
                "week_end": week_end,
                "previous_week": (
                    week_start
                    - timedelta(days=7)
                ),
                "next_week": (
                    week_start
                    + timedelta(days=7)
                ),
                "days": [
                    week_start
                    + timedelta(days=offset)
                    for offset in range(7)
                ],
                "is_submitted": (
                    report.status.code
                    == "SUBMITTED"
                ),
            }
        )

        return context

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        report = self.get_report()

        # Un rapport transmis n'est plus modifiable
        # par son rédacteur.
        if report.status.code == "SUBMITTED":

            messages.warning(
                request,
                (
                    "Ce rapport a déjà été transmis "
                    "et ne peut plus être modifié."
                ),
            )

            return redirect(
                self.get_report_url(
                    report.period_start_date
                )
            )

        formset = self.get_entry_formset(
            data=request.POST
        )

        global_comment = (
            request.POST
            .get(
                "global_comment",
                "",
            )
            .strip()
        )

        # --------------------------------------------------------------
        # Commentaire
        # --------------------------------------------------------------

        if len(global_comment) > 250:

            messages.error(
                request,
                (
                    "Le commentaire ne peut pas "
                    "dépasser 250 caractères."
                ),
            )

            return self.render_to_response(
                self.get_context_data(
                    entry_formset=formset,
                )
            )

        # --------------------------------------------------------------
        # Formset
        # --------------------------------------------------------------

        if not formset.is_valid():

            messages.error(
                request,
                (
                    "Certaines heures saisies "
                    "sont incorrectes."
                ),
            )

            return self.render_to_response(
                self.get_context_data(
                    entry_formset=formset,
                )
            )

        # --------------------------------------------------------------
        # Action
        # --------------------------------------------------------------

        action = request.POST.get(
            "action",
            "save",
        )

        if action not in {
            "save",
            "submit",
        }:
            raise Http404(
                "Action inconnue."
            )

        # --------------------------------------------------------------
        # Persistance
        # --------------------------------------------------------------

        with transaction.atomic():

            formset.save()

            report.global_comment = (
                global_comment
            )

            if action == "submit":

                submitted_status = (
                    self.get_submitted_status()
                )

                report.status = (
                    submitted_status
                )

                report.submitted_at = (
                    timezone.now()
                )

                report.save(
                    update_fields=[
                        "global_comment",
                        "status",
                        "submitted_at",
                        "updated_at",
                    ]
                )

                # --------------------------------------------------
                # Une review par projet présent dans le rapport
                # --------------------------------------------------

                project_ids = (
                    report.lines
                    .filter(
                        is_active=True,
                        task__isnull=False,
                    )
                    .values_list(
                        (
                            "task__work_package__"
                            "project_id"
                        ),
                        flat=True,
                    )
                    .distinct()
                )

                for project_id in project_ids:

                    (
                        ActivityReportProjectReview
                        .objects
                        .get_or_create(
                            activity_report=report,
                            project_id=project_id,
                        )
                    )

            else:

                report.save(
                    update_fields=[
                        "global_comment",
                        "updated_at",
                    ]
                )

        # --------------------------------------------------------------
        # Message
        # --------------------------------------------------------------

        if action == "submit":

            messages.success(
                request,
                (
                    "Le rapport d'activité "
                    "a été transmis."
                ),
            )

        else:

            messages.success(
                request,
                (
                    "Le rapport d'activité "
                    "a été enregistré."
                ),
            )

        return redirect(
            self.get_report_url(
                report.period_start_date
            )
        )

    # ------------------------------------------------------------------
    # Statut
    # ------------------------------------------------------------------

    @staticmethod
    def get_submitted_status():
        """
        Retourne le statut SUBMITTED
        du catalogue ACTIVITY_REPORT.
        """

        status = (
            CatalogValue.objects
            .filter(
                catalog_type__code=(
                    "ACTIVITY_REPORT"
                ),
                catalog_type__is_active=True,
                code="SUBMITTED",
                is_active=True,
            )
            .select_related(
                "catalog_type"
            )
            .first()
        )

        if status is None:

            raise RuntimeError(
                (
                    "Le statut SUBMITTED du "
                    "catalogue ACTIVITY_REPORT "
                    "n'est pas configuré."
                )
            )

        return status

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    @staticmethod
    def get_report_url(
        week_start: date,
    ) -> str:

        base_url = reverse(
            "reporting:week"
        )

        return (
            f"{base_url}"
            f"?week={week_start.isoformat()}"
        )


# ======================================================================
# Liste des rapports à valider
# ======================================================================

class ActivityReportReviewListView(
    LoginRequiredMixin,
    ListView,
):
    """
    Activités projet transmises et disponibles
    pour validation.

    Un chef de projet voit les projets dont il
    est responsable.

    Un administrateur client voit les projets
    de sa société.

    Un administrateur système voit l'ensemble.
    """

    model = ActivityReportProjectReview

    template_name = (
        "reporting/"
        "activity_report_review_list.html"
    )

    context_object_name = "reviews"

    paginate_by = 50

    # ------------------------------------------------------------------
    # Accès
    # ------------------------------------------------------------------

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):
        if not can_review_activity_reports(
            request.user
        ):
            raise Http404(
                "Vous n'êtes pas autorisé "
                "à consulter les rapports à valider."
            )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Queryset
    # ------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        queryset = (
            ActivityReportProjectReview.objects
            .select_related(
                "activity_report",
                "activity_report__user",
                "project",
                "project__company",
                "project__project_manager",
                "reviewed_by",
            )
            .annotate(
                regular_hours_total=Coalesce(
                    Sum(
                        (
                            "activity_report__"
                            "lines__entries__"
                            "regular_hours"
                        ),
                        filter=Q(
                            activity_report__lines__is_active=True,
                            activity_report__lines__task__work_package__project=(
                                models.F("project")
                            ),
                        ),
                    ),
                    Value(0),
                    output_field=DecimalField(
                        max_digits=8,
                        decimal_places=2,
                    ),
                ),
                overtime_hours_total=Coalesce(
                    Sum(
                        (
                            "activity_report__"
                            "lines__entries__"
                            "overtime_hours"
                        ),
                        filter=Q(
                            activity_report__lines__is_active=True,
                            activity_report__lines__task__work_package__project=(
                                models.F("project")
                            ),
                        ),
                    ),
                    Value(0),
                    output_field=DecimalField(
                        max_digits=8,
                        decimal_places=2,
                    ),
                ),
            )
            .annotate(
                total_hours=(
                    models.F("regular_hours_total")
                    + models.F("overtime_hours_total")
                ),
            )
        )

        # --------------------------------------------------------------
        # Périmètre
        # --------------------------------------------------------------

        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(user)
        )

        queryset = queryset.filter(
            project__in=accessible_projects,
        )

        # --------------------------------------------------------------
        # Filtre état
        # --------------------------------------------------------------

        status = (
            self.request.GET.get(
                "status"
            )
        )

        if status in {
            ActivityReportProjectReviewStatus.PENDING,
            ActivityReportProjectReviewStatus.VALIDATED,
        }:

            queryset = queryset.filter(
                status=status
            )

        return queryset.order_by(
            "-activity_report__period_start_date",
            "project__reference",
            "activity_report__user__last_name",
            "activity_report__user__first_name",
        )

    # ------------------------------------------------------------------
    # Contexte
    # ------------------------------------------------------------------

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        context[
            "selected_status"
        ] = (
            self.request.GET.get(
                "status",
                "",
            )
        )

        context[
            "pending_status"
        ] = (
            ActivityReportProjectReviewStatus
            .PENDING
        )

        context[
            "validated_status"
        ] = (
            ActivityReportProjectReviewStatus
            .VALIDATED
        )

        return context
    
   
# ======================================================================
# Détail / validation d'un rapport
# ======================================================================

class ActivityReportReviewDetailView(
    LoginRequiredMixin,
    DetailView,
):
    """
    Consultation d'un rapport transmis
    côté CP / administrateur.

    La review porte sur un projet donné,
    mais le rapport complet de l'utilisateur
    est affiché à titre informatif.
    """

    model = ActivityReportProjectReview

    template_name = (
        "reporting/"
        "activity_report_review_detail.html"
    )

    context_object_name = "review"

    # ------------------------------------------------------------------
    # Accès
    # ------------------------------------------------------------------

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):
        if not can_review_activity_reports(
            request.user
        ):
            raise Http404(
                "Vous n'êtes pas autorisé "
                "à consulter les rapports à valider."
            )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Queryset / sécurité
    # ------------------------------------------------------------------

    def get_queryset(self):

        user = self.request.user

        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(user)
        )

        return (
            ActivityReportProjectReview.objects
            .select_related(
                "activity_report",
                "activity_report__user",
                "project",
                "project__company",
                "project__project_manager",
                "reviewed_by",
            )
            .filter(
                project__in=accessible_projects,
            )
        )
        
    # ------------------------------------------------------------------
    # Entrées du rapport
    # ------------------------------------------------------------------

    def get_report_entries(self):

        report = (
            self.object.activity_report
        )

        project = (
            self.object.project
        )

        return (
            ActivityReportEntry.objects
            .filter(
                activity_report_line__activity_report=(
                    report
                ),
                activity_report_line__is_active=True,
                activity_report_line__task__isnull=False,
                activity_report_line__task__work_package__project=(
                    project
                ),
            )
            .select_related(
                "activity_report_line",
                (
                    "activity_report_line__"
                    "task"
                ),
                (
                    "activity_report_line__"
                    "task__work_package"
                ),
                (
                    "activity_report_line__"
                    "task__work_package__project"
                ),
            )
            .order_by(
                "activity_report_line__created_at",
                "activity_date",
            )
        )
        
    # ------------------------------------------------------------------
    # Présentation
    # ------------------------------------------------------------------

    def build_report_rows(self):
        """
        Regroupe les entrées par ligne et calcule
        les totaux de chaque ligne.
        """

        rows_by_line = {}

        for entry in self.get_report_entries():

            line = (
                entry.activity_report_line
            )

            if line.pk not in rows_by_line:

                if line.task_id:

                    task = line.task

                    project = (
                        task
                        .work_package
                        .project
                    )

                    rows_by_line[
                        line.pk
                    ] = {
                        "line": line,
                        "kind": "task",
                        "label": (
                            f"{task.code} - "
                            f"{task.name}"
                        ),
                        "project": project,
                        "project_label": (
                            f"{project.reference} - "
                            f"{project.name}"
                        ),
                        "is_review_project": (
                            project.pk
                            == self.object.project_id
                        ),
                        "entries": [],
                    }

                else:

                    rows_by_line[
                        line.pk
                    ] = {
                        "line": line,
                        "kind": "activity",
                        "label": (
                            line.line_type.label
                        ),
                        "project": None,
                        "project_label": "",
                        "is_review_project": False,
                        "entries": [],
                    }

            rows_by_line[
                line.pk
            ]["entries"].append(entry)

        # --------------------------------------------------------------
        # Totaux par ligne
        # --------------------------------------------------------------

        for row in rows_by_line.values():

            regular_total = sum(
                (
                    entry.regular_hours
                    for entry
                    in row["entries"]
                ),
                Decimal("0.00"),
            )

            overtime_total = sum(
                (
                    entry.overtime_hours
                    for entry
                    in row["entries"]
                ),
                Decimal("0.00"),
            )

            row[
                "regular_total"
            ] = regular_total

            row[
                "overtime_total"
            ] = overtime_total

            row[
                "total"
            ] = (
                regular_total
                + overtime_total
            )

        return list(
            rows_by_line.values()
        )

    # ------------------------------------------------------------------
    # Contexte
    # ------------------------------------------------------------------

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        report = (
            self.object.activity_report
        )

        rows = (
            self.build_report_rows()
        )

        week_start = (
            report.period_start_date
        )

        week_end = (
            report.period_end_date
        )

        days = [
            week_start
            + timedelta(days=offset)
            for offset in range(7)
        ]

        # --------------------------------------------------------------
        # Totaux semaine
        # --------------------------------------------------------------

        regular_total = sum(
            (
                row["regular_total"]
                for row in rows
            ),
            Decimal("0.00"),
        )

        overtime_total = sum(
            (
                row["overtime_total"]
                for row in rows
            ),
            Decimal("0.00"),
        )

        week_total = (
            regular_total
            + overtime_total
        )

        # --------------------------------------------------------------
        # Totaux par jour
        # --------------------------------------------------------------

        day_totals = []

        for day in days:

            day_total = Decimal(
                "0.00"
            )

            for row in rows:

                for entry in row[
                    "entries"
                ]:

                    if (
                        entry.activity_date
                        != day
                    ):
                        continue

                    day_total += (
                        entry.regular_hours
                        + entry.overtime_hours
                    )

            day_totals.append(
                day_total
            )

        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------

        is_validated = (
            self.object.status
            == ActivityReportProjectReviewStatus.VALIDATED
        )

        user = self.request.user
        project = self.object.project

        is_admin = (
            user.global_role.code
            in {
                "SYSTEM_ADMIN",
                "CLIENT_ADMIN",
            }
        )

        is_project_manager = (
            project.project_manager_id
            == user.pk
        )

        can_validate = (
            not is_validated
            and (
                is_admin
                or is_project_manager
            )
        )

        # --------------------------------------------------------------
        # Contexte
        # --------------------------------------------------------------

        context.update(
            {
                "report": report,
                "report_rows": rows,
                "days": days,
                "day_totals": day_totals,
                "week_start": week_start,
                "week_end": week_end,
                "regular_total": (
                    regular_total
                ),
                "overtime_total": (
                    overtime_total
                ),
                "week_total": (
                    week_total
                ),
                "is_validated": (
                    is_validated
                ),
                "can_validate": (
                    can_validate
                ),
            }
        )

        return context

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        self.object = self.get_object()

        action = request.POST.get(
            "action"
        )

        if action != "validate":
            raise Http404(
                "Action inconnue."
            )

        # --------------------------------------------------------------
        # Déjà validé
        # --------------------------------------------------------------

        if (
            self.object.status
            == ActivityReportProjectReviewStatus.VALIDATED
        ):

            messages.warning(
                request,
                (
                    "Ce rapport est déjà validé "
                    "pour ce projet."
                ),
            )

            return redirect(
                "reporting:review-detail",
                pk=self.object.pk,
            )

        # --------------------------------------------------------------
        # Contrôle des droits
        # --------------------------------------------------------------

        user = request.user
        project = self.object.project

        is_admin = (
            user.global_role.code
            in {
                "SYSTEM_ADMIN",
                "CLIENT_ADMIN",
            }
        )

        is_project_manager = (
            project.project_manager_id
            == user.pk
        )

        if not (
            is_admin
            or is_project_manager
        ):
            raise Http404(
                (
                    "Vous n'êtes pas autorisé "
                    "à valider ce projet."
                )
            )

        # --------------------------------------------------------------
        # Validation
        # --------------------------------------------------------------

        with transaction.atomic():

            self.object.status = (
                ActivityReportProjectReviewStatus
                .VALIDATED
            )

            self.object.reviewed_by = (
                user
            )

            self.object.reviewed_at = (
                timezone.now()
            )

            self.object.full_clean()

            self.object.save(
                update_fields=[
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "updated_at",
                ]
            )

        messages.success(
            request,
            (
                "Le rapport d'activité "
                "a été validé pour ce projet."
            ),
        )

        return redirect(
            "reporting:review-detail",
            pk=self.object.pk,
        )