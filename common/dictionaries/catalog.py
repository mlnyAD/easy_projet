

"""
Dictionnaires métier du domaine Catalog.
"""

from common.constants.catalog import (
    CATALOG_CODE_LENGTH,
    CATALOG_LABEL_LENGTH,
)

CATALOG_TYPE_DICTIONARY = {
    "entity": {
        "name": "catalog_type",
        "label": "Type de catalogue",
        "label_plural": "Types de catalogues",
        "description": (
            "Décrit un type de catalogue utilisé par l'application."
        ),
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "required": True,
        },
        "code": {
            "label": "Code",
            "data_type": "string",
            "required": True,
            "unique": True,
            "max_length": CATALOG_CODE_LENGTH,
        },
        "label": {
            "label": "Libellé",
            "data_type": "string",
            "required": True,
            "max_length": CATALOG_LABEL_LENGTH,
        },
        "description": {
            "label": "Description",
            "data_type": "text",
        },
        "is_hierarchical": {
            "label": "Hiérarchique",
            "data_type": "boolean",
            "required": True,
        },
        "is_editable": {
            "label": "Modifiable",
            "data_type": "boolean",
            "required": True,
        },
        "is_incremental": {
            "label": "Incrémental",
            "data_type": "boolean",
            "required": True,
        },
        "is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
        },
    },
}

CATALOG_VALUE_DICTIONARY = {
    "entity": {
        "name": "catalog_value",
        "label": "Valeur de catalogue",
        "label_plural": "Valeurs de catalogue",
        "description": (
            "Décrit une valeur appartenant à un type de catalogue."
        ),
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "required": True,
        },
        "catalog_type": {
            "label": "Type de catalogue",
            "data_type": "uuid",
            "required": True,
        },
        "code": {
            "label": "Code",
            "data_type": "string",
            "required": True,
            "max_length": CATALOG_CODE_LENGTH,
        },
        "label": {
            "label": "Libellé",
            "data_type": "string",
            "required": True,
            "max_length": CATALOG_LABEL_LENGTH,
        },
        "description": {
            "label": "Description",
            "data_type": "text",
        },
        "parent": {
            "label": "Valeur parente",
            "data_type": "uuid",
        },
        "level": {
            "label": "Niveau",
            "data_type": "integer",
            "required": True,
            "default": 0,
        },
        "sort_order": {
            "label": "Ordre d'affichage",
            "data_type": "integer",
            "required": True,
            "default": 0,
        },
        "is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },
        "is_system": {
            "label": "Système",
            "data_type": "boolean",
            "required": True,
            "default": False,
        },
        "is_default": {
            "label": "Valeur par défaut",
            "data_type": "boolean",
            "required": True,
            "default": False,
        },
    },
}