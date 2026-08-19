

"""
Dictionnaire métier de l'entité WorkPackage.
"""

from common.constants.work_package import (
    WORK_PACKAGE_CODE_LENGTH,
    WORK_PACKAGE_DEFAULT_WORKLOAD_HOURS,
    WORK_PACKAGE_DESCRIPTION_LENGTH,
    WORK_PACKAGE_NAME_LENGTH,
)


WORK_PACKAGE_DICTIONARY = {
    "entity": {
        "name": "work_package",
        "label": "Lot de travaux",
        "label_plural": "Lots de travaux",
        "description": (
            "Lot de travaux rattaché à un projet."
        ),
    },

    "fields": {
        # ------------------------------------------------------------------
        # Identification technique
        # ------------------------------------------------------------------

        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        # ------------------------------------------------------------------
        # Rattachement
        # ------------------------------------------------------------------

        "project": {
            "label": "Projet",
            "data_type": "uuid",
            "required": True,
            "reference": "project",
        },

        # ------------------------------------------------------------------
        # Pilotage
        # ------------------------------------------------------------------

        "status": {
            "label": "Statut",
            "data_type": "uuid",
            "required": True,
            "catalog": "WORK_PACKAGE_STATUS",
        },

        "manager": {
            "label": "Responsable",
            "data_type": "uuid",
            "required": False,
            "reference": "user",
        },

        # ------------------------------------------------------------------
        # Identification
        # ------------------------------------------------------------------

        "code": {
            "label": "Code",
            "data_type": "string",
            "required": False,
            "generated": True,
            "max_length": WORK_PACKAGE_CODE_LENGTH,
        },

        "name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": WORK_PACKAGE_NAME_LENGTH,
        },

        "description": {
            "label": "Description",
            "data_type": "text",
            "required": False,
            "max_length": WORK_PACKAGE_DESCRIPTION_LENGTH,
        },

        # ------------------------------------------------------------------
        # Planning - dates initiales
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # Planning - dates courantes
        # ------------------------------------------------------------------

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
            "default": WORK_PACKAGE_DEFAULT_WORKLOAD_HOURS,
        },

        # ------------------------------------------------------------------
        # État
        # ------------------------------------------------------------------

        "is_active": {
            "label": "Actif",
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