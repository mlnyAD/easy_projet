

from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_LAST_NAME_LENGTH,
    USER_PHONE_LENGTH,
)


CONTACT_DICTIONARY = {
    "entity": {
        "name": "contact",
        "label": "Contact",
        "label_plural": "Contacts",
        "description": (
            "Utilisateur rattaché à un environnement client."
        ),
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },
        "last_name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": USER_LAST_NAME_LENGTH,
        },
        "first_name": {
            "label": "Prénom",
            "data_type": "string",
            "required": True,
            "max_length": USER_FIRST_NAME_LENGTH,
        },
        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": True,
            "max_length": USER_EMAIL_LENGTH,
        },
        "phone": {
            "label": "Téléphone",
            "data_type": "phone",
            "required": False,
            "max_length": USER_PHONE_LENGTH,
        },
        "client": {
            "label": "Client",
            "data_type": "string",
            "required": True,
        },
        "employment_type": {
            "label": "Type d'emploi",
            "data_type": "uuid",
            "required": False,
            "catalog": "USER_EMPLOYMENT_TYPE",
        },
        "client_administration": {
            "label": "Administration client",
            "data_type": "string",
            "required": False,
        },
        "user_is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },
    },
}