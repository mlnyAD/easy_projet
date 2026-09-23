

from __future__ import annotations

from datetime import date, timedelta

from django.db.models import Min
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.projects.models import Project

from .services.calendar import (
    PlanningCalendarService,
)
from .services.consolidation import (
    PlanningConsolidationService,
    PlanningPeriod,
)
from .services.resource_schedule import (
    ResourceScheduleService,
)
from .services.workload import (
    WeeklyWorkloadService,
)
from apps.projects.services.access import (
    ProjectAccessService,
)


class PlanningHomeView(TemplateView):
    """
    Vue principale du planning.

    Elle prépare :
    - le Gantt consolidé ;
    - le plan de charge hebdomadaire par ressource ;
    - le planning ressources ;
    - le calendrier mensuel ;
    - les filtres communs de période et de projet.
    """

    template_name = "planning/planning_home.html"

    DEFAULT_PERIOD_AFTER_DAYS = 120

    VIEW_GANTT = "gantt"
    VIEW_WORKLOAD = "workload"
    VIEW_RESOURCES = "resources"
    VIEW_CALENDAR = "calendar"

    VALID_VIEWS = {
        VIEW_GANTT,
        VIEW_WORKLOAD,
        VIEW_RESOURCES,
        VIEW_CALENDAR,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        state_date = self._get_date_parameter(
            "state_date",
            default=date.today(),
        )

        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
        )

        project = self._get_selected_project(
            accessible_projects=accessible_projects,
        )

        date_from = self._get_date_parameter(
            "date_from",
            default=self._get_default_date_from(
                accessible_projects=accessible_projects,
                project=project,
                state_date=state_date,
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
            date_from, date_to = (
                date_to,
                date_from,
            )

        period = PlanningPeriod(
            date_from=date_from,
            date_to=date_to,
            state_date=state_date,
        )

        selected_view = (
            self._get_selected_view()
        )

        # --------------------------------------------------------------
        # Gantt
        # --------------------------------------------------------------

        planning_data = (
            PlanningConsolidationService()
            .build(
                period=period,
                project=project,
                accessible_projects=accessible_projects,
            )
        )
        # --------------------------------------------------------------
        # Plan de charge
        # --------------------------------------------------------------

        workload_plan = (
            WeeklyWorkloadService()
            .build(
                date_from=date_from,
                date_to=date_to,
                project=project,
                accessible_projects=accessible_projects,
            )
        )
        # --------------------------------------------------------------
        # Planning ressources
        # --------------------------------------------------------------

        resource_schedule = (
            ResourceScheduleService()
            .build(
                date_from=date_from,
                date_to=date_to,
                project=project,
                accessible_projects=accessible_projects,
            )
        )
        # --------------------------------------------------------------
        # Calendrier
        # --------------------------------------------------------------

        calendar_year = (
            self._get_integer_parameter(
                "calendar_year",
                default=state_date.year,
            )
        )

        calendar_month = (
            self._get_integer_parameter(
                "calendar_month",
                default=state_date.month,
            )
        )

        if calendar_year < 1:
            calendar_year = state_date.year

        if not 1 <= calendar_month <= 12:
            calendar_month = state_date.month

        calendar_data = (
            PlanningCalendarService()
            .build(
                year=calendar_year,
                month=calendar_month,
                project=project,
                accessible_projects=accessible_projects,
            )
        )
        # --------------------------------------------------------------
        # Contexte
        # --------------------------------------------------------------

        context.update(
            {
                "planning": planning_data,
                "workload": workload_plan,
                "resource_schedule": resource_schedule,
                "calendar": calendar_data,
                "period": period,
                "selected_project": project,
                "selected_view": selected_view,
                "view_gantt": self.VIEW_GANTT,
                "view_workload": self.VIEW_WORKLOAD,
                "view_resources": self.VIEW_RESOURCES,
                "view_calendar": self.VIEW_CALENDAR,
                "projects": accessible_projects,
            }
        )

        return context

    def _get_selected_project(
        self,
        *,
        accessible_projects,
    ) -> Project | None:
        """
        Retourne le projet sélectionné parmi les projets
        accessibles à l'utilisateur.

        Sans sélection, le planning porte sur l'ensemble
        des projets accessibles.
        """

        project_pk = (
            self.request.GET.get("project")
            or ""
        ).strip()

        if not project_pk:
            return None

        return get_object_or_404(
            accessible_projects,
            pk=project_pk,
        )

    @staticmethod
    def _get_default_date_from(
        *,
        accessible_projects,
        project: Project | None,
        state_date: date,
    ) -> date:
        """
        Retourne la première date de début des projets affichés.

        Sans projet sélectionné, tous les projets actifs accessibles
        participent au calcul. En l'absence de date planifiée, la date
        de situation est retenue afin de conserver une période valide.
        """

        projects = accessible_projects.filter(
            is_active=True,
        )

        if project is not None:
            projects = projects.filter(
                pk=project.pk,
            )

        oldest_start_date = projects.aggregate(
            oldest_start_date=Min(
                "start_date"
            ),
        )["oldest_start_date"]

        return oldest_start_date or state_date
        
    def _get_selected_view(
        self,
    ) -> str:
        """
        Retourne la représentation demandée.

        Valeurs supportées :
        - gantt
        - workload
        - resources
        - calendar

        Le Gantt reste la vue par défaut.
        """

        selected_view = (
            self.request.GET.get("view")
            or self.VIEW_GANTT
        ).strip()

        if selected_view not in self.VALID_VIEWS:
            return self.VIEW_GANTT

        return selected_view

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
            return date.fromisoformat(
                value
            )
        except ValueError:
            return default

    def _get_integer_parameter(
        self,
        name: str,
        *,
        default: int,
    ) -> int:
        """
        Lit un paramètre GET entier.

        Une valeur absente ou invalide reprend la valeur par défaut.
        """

        value = (
            self.request.GET.get(name)
            or ""
        ).strip()

        if not value:
            return default

        try:
            return int(value)
        except ValueError:
            return default
