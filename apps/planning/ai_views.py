

from __future__ import annotations

import json
from datetime import date

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views import View

from apps.integrations.services.openai_services import (
    OpenAIIntegrationError,
)
from apps.projects.services.access import (
    ProjectAccessService,
)

from .services.ai_planning_advisor import PlanningAIAdvisor
from .services.consolidation import (
    PlanningConsolidationService,
    PlanningPeriod,
)
from .services.job_workload import (
    WeeklyJobWorkloadService,
)
from .services.workload import WeeklyWorkloadService


class PlanningAIAnalysisView(View):
    """
    Retourne une analyse IA du planning sélectionné.

    Cette vue est appelée en AJAX par le panneau latéral.
    Elle ne réalise aucune écriture.
    """

    MAX_PERIOD_DAYS = 366

    def post(self, request, *args, **kwargs):
        payload = self._get_payload(
            request=request,
        )

        if payload is None:
            return self._error_response(
                "La requête IA est invalide."
            )

        project_identifier = (
            payload.get("project")
            or ""
        ).strip()

        if not project_identifier:
            return self._error_response(
                "Sélectionnez un projet avant de lancer "
                "l'analyse IA."
            )

        try:
            date_from = self._get_date(
                payload=payload,
                name="date_from",
            )
            date_to = self._get_date(
                payload=payload,
                name="date_to",
            )
            state_date = self._get_date(
                payload=payload,
                name="state_date",
            )
        except ValueError as error:
            return self._error_response(
                str(error)
            )

        if date_to < date_from:
            return self._error_response(
                "La fin de période doit être postérieure "
                "au début de période."
            )

        if (
            (date_to - date_from).days
            > self.MAX_PERIOD_DAYS
        ):
            return self._error_response(
                "La période analysée ne peut pas dépasser "
                "366 jours."
            )

        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                request.user
            )
        )

        try:
            project = (
                accessible_projects
                .filter(
                    pk=project_identifier,
                )
                .first()
            )
        except (ValidationError, ValueError):
            project = None

        if project is None:
            return JsonResponse(
                {
                    "error": (
                        "Ce projet n'est pas accessible."
                    ),
                },
                status=404,
            )

        period = PlanningPeriod(
            date_from=date_from,
            date_to=date_to,
            state_date=state_date,
        )

        try:
            planning = (
                PlanningConsolidationService()
                .build(
                    period=period,
                    project=project,
                    accessible_projects=accessible_projects,
                )
            )

            workload = (
                WeeklyWorkloadService()
                .build(
                    date_from=date_from,
                    date_to=date_to,
                    project=project,
                    accessible_projects=accessible_projects,
                )
            )

            job_workload = (
                WeeklyJobWorkloadService()
                .build(
                    date_from=date_from,
                    date_to=date_to,
                    project=project,
                    accessible_projects=accessible_projects,
                )
            )

            answer = (
                PlanningAIAdvisor()
                .analyze(
                    period=period,
                    planning=planning,
                    workload=workload,
                    job_workload=job_workload,
                    question=(
                        payload.get("question")
                        or ""
                    ),
                    history=payload.get("history"),
                )
            )
        except OpenAIIntegrationError:
            return JsonResponse(
                {
                    "error": (
                        "L'analyse IA est temporairement "
                        "indisponible."
                    ),
                },
                status=502,
            )

        return JsonResponse(
            {
                "answer": answer,
                "project": {
                    "reference": project.reference,
                    "name": project.name,
                },
            }
        )

    @staticmethod
    def _get_payload(
        *,
        request,
    ) -> dict | None:
        try:
            payload = json.loads(
                request.body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return None

        if not isinstance(payload, dict):
            return None

        return payload

    @staticmethod
    def _get_date(
        *,
        payload: dict,
        name: str,
    ) -> date:
        value = (
            payload.get(name)
            or ""
        ).strip()

        if not value:
            raise ValueError(
                f"Le paramètre {name!r} est obligatoire."
            )

        try:
            return date.fromisoformat(
                value
            )
        except ValueError as error:
            raise ValueError(
                f"Le paramètre {name!r} est invalide."
            ) from error

    @staticmethod
    def _error_response(
        message: str,
    ) -> JsonResponse:
        return JsonResponse(
            {
                "error": message,
            },
            status=400,
        )