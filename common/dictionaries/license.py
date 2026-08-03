

from common.constants.license import (
    LICENSE_REFERENCE_LENGTH,
)


LICENSE_DICTIONARY = {
    "entity": {
        "name": "license",
        "label": "Licence",
        "label_plural": "Licences",
        "description": (
            "Licence attribuée à un environnement client Easy Projet."
        ),
    },

    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "company_name": {
            "label": "Société",
            "data_type": "string",
            "required": True,
            "generated": True,
        },

        "reference": {
            "label": "Référence commerciale",
            "data_type": "string",
            "required": True,
            "max_length": LICENSE_REFERENCE_LENGTH,
        },

        "status_label": {
            "label": "Statut",
            "data_type": "string",
            "required": True,
            "generated": True,
        },

        "project_capacity": {
            "label": "Capacité",
            "data_type": "integer",
            "required": True,
        },

        "granted_at": {
            "label": "Date d'attribution",
            "data_type": "date",
            "required": True,
        },

        "expiration_date": {
            "label": "Date d'expiration",
            "data_type": "date",
            "required": False,
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