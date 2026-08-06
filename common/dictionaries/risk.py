

from common.constants.risk import (
    RISK_DESCRIPTION_LENGTH,
    RISK_PLANNED_ACTIONS_LENGTH,
    RISK_REFERENCE_LENGTH,
    RISK_TITLE_LENGTH,
)

RISK_DICTIONARY = {
    "entity": {
        "name": "risk",
        "label": "Risque",
        "label_plural": "Risques",
        "description": (
            "Risque ou opportunité associé à un projet."
        ),
    },

    "fields": {

        # ------------------------------------------------------------------
        # Identifiant
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

        "owner": {
            "label": "Pilote",
            "data_type": "uuid",
            "required": False,
            "reference": "user",
        },

        # ------------------------------------------------------------------
        # Classification
        # ------------------------------------------------------------------

        "origin": {
            "label": "Origine",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_ORIGIN",
        },

        "risk_type": {
            "label": "Type",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_TYPE",
        },

        "risk_class": {
            "label": "Classe",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_CLASS",
        },

        "impact": {
            "label": "Impact",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_IMPACT",
        },

        "severity": {
            "label": "Gravité",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_GRAVITY",
        },

        "probability": {
            "label": "Probabilité",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_PROBABILITY",
        },

        "status": {
            "label": "Etat",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_STATE",
        },

        "criticality": {
            "label": "Criticité",
            "data_type": "uuid",
            "required": True,
            "catalog": "RISK_CRITICALITY",
        },

        "review_frequency": {
            "label": "Fréquence de revue",
            "data_type": "uuid",
            "required": False,
            "catalog": "RISK_REVIEW_FREQUENCY",
        },

        # ------------------------------------------------------------------
        # Identification
        # ------------------------------------------------------------------

        "reference": {
            "label": "Référence",
            "data_type": "string",
            "required": False,
            "generated": True,
            "max_length": RISK_REFERENCE_LENGTH,
        },

        "title": {
            "label": "Titre",
            "data_type": "string",
            "required": True,
            "max_length": RISK_TITLE_LENGTH,
        },

        "description": {
            "label": "Description",
            "data_type": "text",
            "required": False,
            "max_length": RISK_DESCRIPTION_LENGTH,
        },

        # ------------------------------------------------------------------
        # Evaluation
        # ------------------------------------------------------------------

        "occurrence_date": {
            "label": "Date d'apparition",
            "data_type": "date",
            "required": False,
        },

        "closure_date": {
            "label": "Date de clôture",
            "data_type": "date",
            "required": False,
        },

        "estimated_cost": {
            "label": "Coût estimé",
            "data_type": "decimal",
            "required": False,
        },

        "last_review_date": {
            "label": "Dernière revue",
            "data_type": "date",
            "required": False,
        },

        "planned_actions": {
            "label": "Actions prévues",
            "data_type": "text",
            "required": False,
            "max_length": RISK_PLANNED_ACTIONS_LENGTH,
        },

        # ------------------------------------------------------------------
        # Etat
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