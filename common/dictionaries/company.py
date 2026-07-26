

from common.constants.company import (
    COMPANY_ADDRESS_LENGTH,
    COMPANY_CITY_LENGTH,
    COMPANY_COUNTRY_LENGTH,
    COMPANY_EMAIL_LENGTH,
    COMPANY_NAME_LENGTH,
    COMPANY_PHONE_LENGTH,
    COMPANY_POSTAL_CODE_LENGTH,
    COMPANY_SIRET_LENGTH,
    COMPANY_VAT_NUMBER_LENGTH,
)

COMPANY_DICTIONARY = {
    "entity": {
        "name": "company",
        "label": "Société",
        "label_plural": "Sociétés",
        "description": "Société intervenant dans Easy Projet.",
    },

    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "name": {
            "label": "Nom",
            "data_type": "string",
            "required": True,
            "max_length": COMPANY_NAME_LENGTH,
        },

        "siret": {
            "label": "SIRET",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_SIRET_LENGTH,
        },

        "vat_number": {
            "label": "Numéro de TVA intracommunautaire",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_VAT_NUMBER_LENGTH,
        },

        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": False,
            "max_length": COMPANY_EMAIL_LENGTH,
        },

        "phone": {
            "label": "Téléphone",
            "data_type": "phone",
            "required": False,
            "max_length": COMPANY_PHONE_LENGTH,
        },

        "address_1": {
            "label": "Adresse",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_ADDRESS_LENGTH,
        },

        "address_2": {
            "label": "Complément d’adresse",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_ADDRESS_LENGTH,
        },

        "address_3": {
            "label": "Complément d’adresse 2",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_ADDRESS_LENGTH,
        },

        "postal_code": {
            "label": "Code postal",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_POSTAL_CODE_LENGTH,
        },

        "city": {
            "label": "Ville",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_CITY_LENGTH,
        },

        "country": {
            "label": "Pays",
            "data_type": "string",
            "required": False,
            "max_length": COMPANY_COUNTRY_LENGTH,
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