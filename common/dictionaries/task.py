

"""
Dictionnaire métier de l'entité Task.
"""

from common.constants.task import (
    TASK_CODE_LENGTH,
    TASK_DEFAULT_PLANNED_WORKLOAD_HOURS,
    TASK_DEFAULT_PROGRESS_PERCENT,
    TASK_DEFAULT_REMAINING_WORKLOAD_HOURS,
    TASK_DESCRIPTION_LENGTH,
    TASK_NAME_LENGTH,
)


TASK_DICTIONARY = {
    "entity": {
        "name": "task",
        "label": "Tâche",
        "label_plural": "Tâches",
        "description": (
            "Tâche opérationnelle rattachée à un lot de travaux."
        ),
    },

    "fields": {
        # ------------------------------------------------------------------
        # Identification
        # ------------------------------------------------------------------

        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "work_package": {
            "label": "Lot de travaux",
            "data_type": "uuid",
            "required": True,
            "reference": "work_package",
        },

        "status": {
            "label": "Statut",
            "data_type": "uuid",
            "required": True,
            "catalog": "TASK_STATUS",
        },

        "code": {
            "label": "Code",
            "data_type": "string",
            "required": False,
            "generated": True,
            "max_length": TASK_CODE_LENGTH,
        },

        "name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": TASK_NAME_LENGTH,
        },

        "description": {
            "label": "Description",
            "data_type": "text",
            "required": False,
            "max_length": TASK_DESCRIPTION_LENGTH,
        },

        # ------------------------------------------------------------------
        # Planning
        # ------------------------------------------------------------------

        "planned_start_date": {
            "label": "Début planifié",
            "data_type": "date",
            "required": False,
        },

        "planned_end_date": {
            "label": "Fin planifiée",
            "data_type": "date",
            "required": False,
        },

        "updated_start_date": {
            "label": "Début actualisé",
            "data_type": "date",
            "required": False,
        },

        "updated_end_date": {
            "label": "Fin actualisée",
            "data_type": "date",
            "required": False,
        },

        "effective_start_date": {
            "label": "Début",
            "data_type": "date",
            "required": False,
            "generated": True,
        },

        "effective_end_date": {
            "label": "Fin",
            "data_type": "date",
            "required": False,
            "generated": True,
        },

        "planned_workload_hours": {
            "label": "Charge planifiée (h)",
            "data_type": "integer",
            "required": True,
            "default": TASK_DEFAULT_PLANNED_WORKLOAD_HOURS,
        },

        "remaining_workload_hours": {
            "label": "Reste à faire estimé (h)",
            "data_type": "integer",
            "required": True,
            "default": TASK_DEFAULT_REMAINING_WORKLOAD_HOURS,
        },

        "progress_percent": {
            "label": "Avancement (%)",
            "data_type": "integer",
            "required": True,
            "default": TASK_DEFAULT_PROGRESS_PERCENT,
        },

        # ------------------------------------------------------------------
        # État
        # ------------------------------------------------------------------

        "is_active": {
            "label": "Tâche active",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },

        # ------------------------------------------------------------------
        # Traçabilité
        # ------------------------------------------------------------------

        "created_at": {
            "label": "Date de création",
            "data_type": "datetime",
            "required": True,
            "generated": True,
        },

        "updated_at": {
            "label": "Dernière modification",
            "data_type": "datetime",
            "required": True,
            "generated": True,
        },
    },
}