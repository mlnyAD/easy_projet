

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
            "max_length": 150,
        },

        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": False,
            "max_length": 254,
        },

        "phone": {
            "label": "Téléphone",
            "data_type": "phone",
            "required": False,
            "max_length": 20,
        },

        "address_1": {
            "label": "Adresse",
            "data_type": "string",
            "required": False,
            "max_length": 150,
        },

        "address_2": {
            "label": "Complément d’adresse",
            "data_type": "string",
            "required": False,
            "max_length": 150,
        },

        "address_3": {
            "label": "Complément d’adresse 2",
            "data_type": "string",
            "required": False,
            "max_length": 150,
        },

        "postal_code": {
            "label": "Code postal",
            "data_type": "string",
            "required": False,
            "max_length": 20,
        },

        "city": {
            "label": "Ville",
            "data_type": "string",
            "required": False,
            "max_length": 100,
        },

        "country": {
            "label": "Pays",
            "data_type": "string",
            "required": False,
            "max_length": 100,
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