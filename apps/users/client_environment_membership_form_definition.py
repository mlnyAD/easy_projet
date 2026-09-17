

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


CLIENT_ENVIRONMENT_MEMBERSHIP_FORM_DEFINITION = (
    FormDefinition(
        name="client_environment_membership",
        title="Rattachement à un environnement client",

        sections=[
            SectionDefinition(
                title="Rattachement",
                fields=[
                    FieldDefinition(
                        name="client_environment",
                    ),
                    FieldDefinition(
                        name="employment_type",
                        required=False,
                    ),
                    FieldDefinition(
                        name="is_active",
                        required=False,
                        width=FieldWidth.FULL,
                        checked_label="Actif",
                        unchecked_label="Inactif",
                    ),
                ],
            ),

            SectionDefinition(
                title="Droits d'administration",
                fields=[
                    FieldDefinition(
                        name=(
                            "is_client_admin_responsible"
                        ),
                        required=False,
                        width=FieldWidth.FULL,
                        checked_label=(
                            "Administrateur client titulaire"
                        ),
                        unchecked_label=(
                            "Non titulaire"
                        ),
                    ),
                    FieldDefinition(
                        name=(
                            "is_client_admin_delegate"
                        ),
                        required=False,
                        width=FieldWidth.FULL,
                        checked_label=(
                            "Administrateur client délégué"
                        ),
                        unchecked_label=(
                            "Non délégué"
                        ),
                    ),
                ],
            ),
        ],
    )
)