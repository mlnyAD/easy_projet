

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


USER_FORM_DEFINITION = FormDefinition(
    name="user",
    title="Utilisateur",
    sections=[
        SectionDefinition(
            title="Identité",
            fields=[
                FieldDefinition(name="last_name"),
                FieldDefinition(name="first_name"),
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
            title="Coordonnées",
            fields=[
                FieldDefinition(name="email"),
                FieldDefinition(name="phone"),
                FieldDefinition(name="mobile"),
            ],
        ),
        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(name="company"),
                FieldDefinition(name="employment_type"),
                FieldDefinition(name="job"),
            ],
        ),
        SectionDefinition(
            title="Autorisations",
            fields=[
                FieldDefinition(name="global_role"),
                FieldDefinition(name="access_level"),
            ],
        ),
        SectionDefinition(
            title="Préférences",
            fields=[
                FieldDefinition(name="theme"),
            ],
        ),
    ],
)