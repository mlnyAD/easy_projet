

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


ACCOUNT_FORM_DEFINITION = FormDefinition(
    name="account",
    title="Mon compte",
    sections=[
        SectionDefinition(
            title="Identité",
            fields=[
                FieldDefinition(
                    name="photo",
                    required=False,
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(name="first_name"),
                FieldDefinition(name="last_name"),
                FieldDefinition(name="email"),
                FieldDefinition(name="company_display"),
                FieldDefinition(name="global_role_display"),
            ],
        ),
        SectionDefinition(
            title="Sécurité",
            fields=[
                FieldDefinition(
                    name="current_password",
                    required=False,
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="new_password",
                    required=False,
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="new_password_confirmation",
                    required=False,
                    width=FieldWidth.FULL,
                ),
            ],
        ),
    ],
)