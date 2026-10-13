

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from apps.integrations.services.openai_services import (
    OpenAIIntegrationService,
)

from .consolidation import (
    PlanningData,
    PlanningPeriod,
)
from .job_workload import JobWorkloadPlan
from .workload import WorkloadPlan


class PlanningAIAdvisor:
    """
    Produit des recommandations de planning à partir des données
    déjà calculées par les services de planification.

    Cette classe n'écrit jamais en base de données.
    """

    MAX_CONVERSATION_MESSAGES = 6
    MAX_MESSAGE_LENGTH = 1_500
    MAX_TASKS = 120
    MAX_JOB_REQUIREMENTS = 160
    MAX_RESOURCE_WEEKS = 240

    def analyze(
        self,
        *,
        period: PlanningPeriod,
        planning: PlanningData,
        workload: WorkloadPlan,
        job_workload: JobWorkloadPlan,
        question: str,
        history: object,
    ) -> str:
        """
        Retourne une réponse IA à partir du contexte de planification.
        """

        context = self._build_context(
            period=period,
            planning=planning,
            workload=workload,
            job_workload=job_workload,
        )

        conversation = self._normalize_history(
            history=history,
        )

        normalized_question = (
            question.strip()
            or (
                "Analyse ce planning et indique les principaux "
                "risques, incohérences et actions prioritaires."
            )
        )

        input_text = json.dumps(
            {
                "donnees_planning": context,
                "conversation_precedente": conversation,
                "question_utilisateur": normalized_question,
            },
            ensure_ascii=False,
            indent=2,
        )

        return OpenAIIntegrationService.generate_text(
            instructions=(
                "Tu es un assistant de planification de chantier. "
                "Tu réponds exclusivement en français. "
                "Analyse uniquement les données fournies. "
                "Ne suppose jamais une information absente. "
                "Ne propose aucune modification automatique. "
                "Présente la réponse avec les rubriques suivantes : "
                "Synthèse, Alertes prioritaires, Recommandations, "
                "Points à confirmer. "
                "Pour chaque recommandation, explique brièvement "
                "le constat et l'action proposée. "
                "Si les données sont insuffisantes, indique-le."
            ),
            input_text=input_text,
        )

    def _build_context(
        self,
        *,
        period: PlanningPeriod,
        planning: PlanningData,
        workload: WorkloadPlan,
        job_workload: JobWorkloadPlan,
    ) -> dict:
        tasks = [
            {
                "code": item.code,
                "nom": item.name,
                "debut": self._format_date(item.start_date),
                "fin": self._format_date(item.end_date),
                "charge_prevue_heures": item.planned_workload_hours,
                "heures_realisees": self._format_decimal(
                    item.actual_hours
                ),
                "avancement_pourcent": item.progress_percent,
                "ressources": list(item.resources),
            }
            for item in planning.items
            if item.object_type == "task"
        ]

        resource_weeks = []

        for resource in workload.resources:
            for cell in resource.cells:
                if cell.status == "empty":
                    continue

                resource_weeks.append(
                    {
                        "ressource": (
                            f"{resource.last_name} "
                            f"{resource.first_name}"
                        ).strip(),
                        "semaine": cell.week.label,
                        "du": self._format_date(
                            cell.week.start_date
                        ),
                        "au": self._format_date(
                            cell.week.end_date
                        ),
                        "charge_pourcent": self._format_decimal(
                            cell.workload_percent
                        ),
                        "etat": self._get_workload_label(
                            cell.status
                        ),
                    }
                )

        job_requirements = [
            {
                "tache": requirement.task_code,
                "nom_tache": requirement.task_name,
                "metier": requirement.job_label,
                "charge_totale_heures": self._format_decimal(
                    requirement.planned_workload_hours
                ),
                "charge_visible_heures": self._format_decimal(
                    requirement.visible_workload_hours
                ),
            }
            for requirement in job_workload.requirements
        ]

        return {
            "periode": {
                "debut": self._format_date(period.date_from),
                "fin": self._format_date(period.date_to),
                "date_situation": self._format_date(
                    period.state_date
                ),
            },
            "taches": tasks[:self.MAX_TASKS],
            "taches_tronquees": len(tasks) > self.MAX_TASKS,
            "charges_ressources": (
                resource_weeks[:self.MAX_RESOURCE_WEEKS]
            ),
            "charges_ressources_tronquees": (
                len(resource_weeks)
                > self.MAX_RESOURCE_WEEKS
            ),
            "besoins_metiers": (
                job_requirements[
                    :self.MAX_JOB_REQUIREMENTS
                ]
            ),
            "besoins_metiers_tronques": (
                len(job_requirements)
                > self.MAX_JOB_REQUIREMENTS
            ),
        }

    def _normalize_history(
        self,
        *,
        history: object,
    ) -> list[dict[str, str]]:
        if not isinstance(history, list):
            return []

        messages: list[dict[str, str]] = []

        for item in history[-self.MAX_CONVERSATION_MESSAGES:]:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role not in {"user", "assistant"}:
                continue

            if not isinstance(content, str):
                continue

            normalized_content = content.strip()

            if not normalized_content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": normalized_content[
                        :self.MAX_MESSAGE_LENGTH
                    ],
                }
            )

        return messages

    @staticmethod
    def _format_date(value: date | None) -> str | None:
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _format_decimal(
        value: Decimal,
    ) -> float:
        return float(value)

    @staticmethod
    def _get_workload_label(status: str) -> str:
        labels = {
            "available": "sous-charge",
            "nominal": "charge nominale",
            "overload": "surcharge",
        }

        return labels.get(
            status,
            status,
        )