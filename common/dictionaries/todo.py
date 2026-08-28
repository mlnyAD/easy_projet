

from common.constants import TITLE_LENGTH


TODO_DICTIONARY = {
    "entity": {
        "name": "todo_action",
        "label": "Action Todo",
        "label_plural": "Actions Todo",
        "description": (
            "Action personnelle ou assignée à un utilisateur."
        ),
    },

    "fields": {

        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "status_label": {
            "label": "État",
            "data_type": "string",
            "required": True,
        },

        "title": {
            "label": "Action",
            "data_type": "string",
            "required": True,
            "max_length": TITLE_LENGTH,
        },

        "due_date": {
            "label": "Échéance",
            "data_type": "date",
            "required": False,
        },

        "project": {
            "label": "Projet",
            "data_type": "uuid",
            "required": False,
            "reference": "project",
        },

        "origin_label": {
            "label": "Origine",
            "data_type": "string",
            "required": True,
        },

        "role_label": {
            "label": "Rôle",
            "data_type": "string",
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