

from common.constants.meeting import (
    MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH,
)


MEETING_PARTICIPANT_DICTIONARY = {
    "entity": {
        "name": "meeting_participant",
        "label": "Participant à une réunion",
        "label_plural": "Participants aux réunions",
        "description": (
            "Participant interne ou externe invité à une réunion."
        ),
    },

    "fields": {
        # ----------------------------------------------------------
        # Identifiant
        # ----------------------------------------------------------

        "id": {
            "label": "Identifiant",
            "data_type": "uuid",
            "identifier": True,
            "generated": True,
        },

        # ----------------------------------------------------------
        # Rattachement
        # ----------------------------------------------------------

        "meeting": {
            "label": "Réunion",
            "data_type": "uuid",
            "required": True,
            "reference": "meeting",
        },

        # ----------------------------------------------------------
        # Participant
        # ----------------------------------------------------------

        "participant": {
            "label": "Participant interne",
            "data_type": "uuid",
            "required": False,
            "reference": "user",
        },

        "external_name": {
            "label": "Nom du participant externe",
            "data_type": "string",
            "required": False,
            "max_length": (
                MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH
            ),
        },

        "external_email": {
            "label": "Email du participant externe",
            "data_type": "string",
            "required": False,
            "max_length": (
                MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH
            ),
        },

        # ----------------------------------------------------------
        # Invitation
        # ----------------------------------------------------------

        "invitation_response": {
            "label": "Réponse à l'invitation",
            "data_type": "uuid",
            "required": False,
            "catalog": "MEETING_INVITATION_RESPONSE",
        },

        # ----------------------------------------------------------
        # État
        # ----------------------------------------------------------

        "is_active": {
            "label": "Actif",
            "data_type": "boolean",
            "required": True,
            "default": True,
        },

        # ----------------------------------------------------------
        # Traçabilité
        # ----------------------------------------------------------

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