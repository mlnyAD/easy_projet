

from common.constants.meeting import (
    MEETING_COMMENTS_LENGTH,
    MEETING_LOCATION_LENGTH,
    MEETING_REFERENCE_LENGTH,
    MEETING_SUBJECT_LENGTH,
)


MEETING_DICTIONARY = {
    "entity": {
        "name": "meeting",
        "label": "Réunion",
        "label_plural": "Réunions",
        "description": (
            "Réunion organisée dans le cadre d'un projet."
        ),
    },

    "fields": {
        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        "project": {
            "label": "Projet",
            "data_type": "uuid",
            "required": True,
            "reference": "project",
        },

        "organizer": {
            "label": "Organisateur",
            "data_type": "uuid",
            "required": True,
            "reference": "user",
        },

        "status": {
            "label": "État",
            "data_type": "uuid",
            "required": True,
            "catalog": "MEETING_STATUS",
        },

        "reference": {
            "label": "Référence",
            "data_type": "string",
            "required": False,
            "generated": True,
            "max_length": MEETING_REFERENCE_LENGTH,
        },

        "subject": {
            "label": "Objet",
            "data_type": "string",
            "required": True,
            "max_length": MEETING_SUBJECT_LENGTH,
        },

        "scheduled_at": {
            "label": "Date et heure",
            "data_type": "datetime",
            "required": True,
        },

        "duration_hours": {
            "label": "Durée (h)",
            "data_type": "decimal",
            "required": False,
        },

        "location": {
            "label": "Lieu",
            "data_type": "string",
            "required": False,
            "max_length": MEETING_LOCATION_LENGTH,
        },

        "agenda": {
            "label": "Ordre du jour",
            "data_type": "text",
            "required": False,
            "max_length": MEETING_COMMENTS_LENGTH,
        },

        "notes": {
            "label": "Notes de convocation",
            "data_type": "text",
            "required": False,
            "max_length": MEETING_COMMENTS_LENGTH,
        },

        "comments": {
            "label": "Commentaires internes",
            "data_type": "text",
            "required": False,
            "max_length": MEETING_COMMENTS_LENGTH,
        },

        "is_active": {
            "label": "Actif",
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