

from common.constants.integration import (
    INTEGRATION_CODE_LENGTH,
    INTEGRATION_CREDENTIAL_REFERENCE_LENGTH,
    INTEGRATION_NAME_LENGTH,
)


EXTERNAL_INTEGRATION_DICTIONARY = {
    "entity": {
        "name": "external_integration",
        "label": "Intégration externe",
        "label_plural": "Intégrations externes",
        "description": (
            "Service externe disponible dans un environnement client."
        ),
    },

    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "client_environment": {
            "label": "Environnement client",
            "data_type": "uuid",
            "required": True,
            "reference": "client_environment",
        },

        "service_type": {
            "label": "Type de service",
            "data_type": "uuid",
            "required": True,
            "catalog": "INTEGRATION_SERVICE_TYPE",
        },

        "provider": {
            "label": "Fournisseur",
            "data_type": "uuid",
            "required": True,
            "catalog": "INTEGRATION_PROVIDER",
        },

        "connection_status": {
            "label": "État de connexion",
            "data_type": "uuid",
            "required": True,
            "catalog": "INTEGRATION_CONNECTION_STATUS",
        },

        "code": {
            "label": "Code",
            "data_type": "string",
            "required": True,
            "max_length": INTEGRATION_CODE_LENGTH,
        },

        "name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": INTEGRATION_NAME_LENGTH,
        },

        "priority": {
            "label": "Priorité",
            "data_type": "integer",
            "required": True,
            "default": 100,
        },

        "credential_reference": {
            "label": "Référence des credentials",
            "data_type": "string",
            "required": False,
            "max_length": (
                INTEGRATION_CREDENTIAL_REFERENCE_LENGTH
            ),
        },

        "is_active": {
            "label": "Active",
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