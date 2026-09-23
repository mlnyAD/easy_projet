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
        "initial_start_date": {
            "label": "Début initial",
            "data_type": "date",
            "required": False,
        },
        "initial_end_date": {
            "label": "Fin initiale",
            "data_type": "date",
            "required": False,
        },
        "start_date": {
            "label": "Début",
            "data_type": "date",
            "required": False,
        },
        "end_date": {
            "label": "Fin",
            "data_type": "date",
            "required": False,
        },
        "planned_workload_hours": {
            "label": "Charge planifiée (h)",
            "data_type": "integer",
            "required": True,
            "default": TASK_DEFAULT_PLANNED_WORKLOAD_HOURS,
        },
        "consumed_workload_hours": {
            "label": "Consommé (h)",
            "data_type": "decimal",
            "required": False,
            "generated": True,
        },
        "remaining_workload_hours": {
            "label": "Reste à faire estimé (h)",
            "data_type": "decimal",
            "required": True,
            "default": TASK_DEFAULT_REMAINING_WORKLOAD_HOURS,
        },
        "progress_percent": {
            "label": "Avancement (%)",
            "data_type": "integer",
            "required": True,
            "default": TASK_DEFAULT_PROGRESS_PERCENT,
        },
        "is_active": {
            "label": "Tâche active",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },
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
