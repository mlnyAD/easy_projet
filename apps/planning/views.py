

from __future__ import annotations

from datetime import date, timedelta

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.projects.models import Project

from .services.consolidation import (
    PlanningConsolidationService,
    PlanningPeriod,
)


class PlanningHomeView(TemplateView):
    """
    Vue principale du planning.

    Cette première version construit les données consolidées
    nécessaires aux futures représentations du planning.
    """

    template_name = "planning/planning_home.html"

    DEFAULT_PERIOD_BEFORE_DAYS = 30
    DEFAULT_PERIOD_AFTER_DAYS = 90

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        state_date = self._get_date_parameter(
            "state_date",
            default=date.today(),
        )

        date_from = self._get_date_parameter(
            "date_from",
            default=(
                state_date
                - timedelta(
                    days=self.DEFAULT_PERIOD_BEFORE_DAYS
                )
            ),
        )

        date_to = self._get_date_parameter(
            "date_to",
            default=(
                state_date
                + timedelta(
                    days=self.DEFAULT_PERIOD_AFTER_DAYS
                )
            ),
        )

        if date_to < date_from:
            date_from, date_to = date_to, date_from

        period = PlanningPeriod(
            date_from=date_from,
            date_to=date_to,
            state_date=state_date,
        )

        project = self._get_selected_project()

        planning_data = (
            PlanningConsolidationService().build(
                period=period,
                project=project,
            )
        )

        context["planning"] = planning_data
        context["period"] = period

        context["selected_project"] = project

        context["projects"] = (
            Project.objects
            .filter(is_active=True)
            .order_by(
                "reference",
                "name",
            )
        )

        return context

    def _get_selected_project(
        self,
    ) -> Project | None:
        """
        Retourne le projet sélectionné dans les paramètres GET.

        En l'absence de sélection, le planning porte sur
        l'ensemble des projets actifs.
        """

        project_pk = (
            self.request.GET.get("project")
            or ""
        ).strip()

        if not project_pk:
            return None

        return get_object_or_404(
            Project.objects.filter(is_active=True),
            pk=project_pk,
        )

    def _get_date_parameter(
        self,
        name: str,
        *,
        default: date,
    ) -> date:
        """
        Lit un paramètre GET au format ISO YYYY-MM-DD.

        Une valeur absente ou invalide reprend la valeur par défaut.
        """

        value = (
            self.request.GET.get(name)
            or ""
        ).strip()

        if not value:
            return default

        try:
            return date.fromisoformat(value)
        except ValueError:
            return default