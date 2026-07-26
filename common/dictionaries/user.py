

from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_INITIALS_LENGTH,
    USER_LANGUAGE_LENGTH,
    USER_LAST_NAME_LENGTH,
    USER_MOBILE_LENGTH,
    USER_PHONE_LENGTH,
    USER_PREFERRED_NAME_LENGTH,
    USER_THEME_LENGTH,
    USER_TIMEZONE_LENGTH,
)

USER_DICTIONARY = {
    "entity": {
        "name": "user",
        "label": "Utilisateur",
        "label_plural": "Utilisateurs",
        "description": "Utilisateur autorisé à accéder à Easy Projet.",
    },

    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        # ------------------------------------------------------------------
        # Identité
        # ------------------------------------------------------------------

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

        "preferred_name": {
            "label": "Prénom d’usage",
            "data_type": "string",
            "required": False,
            "max_length": USER_PREFERRED_NAME_LENGTH,
        },

        "initials": {
            "label": "Initiales",
            "data_type": "string",
            "required": True,
            "generated": True,
            "max_length": USER_INITIALS_LENGTH,
        },

        "photo": {
            "label": "Photo",
            "data_type": "image",
            "required": False,
        },

        # ------------------------------------------------------------------
        # Coordonnées
        # ------------------------------------------------------------------

        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": True,
            "unique": True,
            "max_length": USER_EMAIL_LENGTH,
        },

        "phone": {
            "label": "Téléphone",
            "data_type": "phone",
            "required": False,
            "max_length": USER_PHONE_LENGTH,
        },

        "mobile": {
            "label": "Téléphone mobile",
            "data_type": "phone",
            "required": False,
            "max_length": USER_MOBILE_LENGTH,
        },

        # ------------------------------------------------------------------
        # Rattachement
        # ------------------------------------------------------------------

        "company": {
            "label": "Société",
            "data_type": "uuid",
            "required": True,
            "reference": "company",
        },

        "employment_type": {
            "label": "Type d’emploi",
            "data_type": "uuid",
            "required": False,
            "catalog": "USER_EMPLOYMENT_TYPE",
        },

        "job": {
            "label": "Métier",
            "data_type": "uuid",
            "required": False,
            "catalog": "USER_JOB",
        },

        # ------------------------------------------------------------------
        # Autorisations
        # ------------------------------------------------------------------

        "global_role": {
            "label": "Rôle global",
            "data_type": "uuid",
            "required": True,
            "catalog": "USER_GLOBAL_ROLE",
        },

        "access_level": {
            "label": "Niveau d’accès",
            "data_type": "uuid",
            "required": True,
            "catalog": "USER_LEVEL_ACCESS",
        },

        "is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },

        # ------------------------------------------------------------------
        # Préférences
        # ------------------------------------------------------------------

        "language": {
            "label": "Langue",
            "data_type": "string",
            "required": False,
            "max_length": USER_LANGUAGE_LENGTH,
        },

        "timezone": {
            "label": "Fuseau horaire",
            "data_type": "string",
            "required": False,
            "max_length": USER_TIMEZONE_LENGTH,
        },

        "theme": {
            "label": "Thème",
            "data_type": "string",
            "required": False,
            "max_length": USER_THEME_LENGTH,
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