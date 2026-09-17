

CLIENT_ENVIRONMENT_MEMBERSHIP_DICTIONARY = {
    "entity": {
        "name": "client_environment_membership",
        "label": "Rattachement à un environnement client",
        "label_plural": (
            "Rattachements aux environnements clients"
        ),
        "description": (
            "Droit de présence et d'administration "
            "d'un utilisateur dans un environnement client."
        ),
    },
    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },
        "user": {
            "label": "Utilisateur",
            "data_type": "uuid",
            "required": True,
            "reference": "user",
        },
        "client_environment": {
            "label": "Environnement client",
            "data_type": "uuid",
            "required": True,
            "reference": "client_environment",
        },
        "employment_type": {
            "label": "Type d'emploi",
            "data_type": "uuid",
            "required": False,
            "catalog": "USER_EMPLOYMENT_TYPE",
        },
        "is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },
        "is_client_admin": {
            "label": "Administrateur client",
            "data_type": "boolean",
            "required": True,
            "default": False,
        },
        "is_client_admin_responsible": {
            "label": "Administrateur client titulaire",
            "data_type": "boolean",
            "required": True,
            "default": False,
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