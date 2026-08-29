

from framework.form import (
    FieldDefinition,
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


MEETING_FORM_DEFINITION = FormDefinition(
    name="meeting",
    title="Réunion",
    sections=[
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="project",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="organizer",
                ),
                FieldDefinition(
                    name="status",
                ),
                FieldDefinition(
                    name="reference",
                ),
                FieldDefinition(
                    name="subject",
                ),
            ],
        ),
        SectionDefinition(
            title="Organisation",
            fields=[
                FieldDefinition(
                    name="scheduled_at",
                ),
                FieldDefinition(
                    name="duration_hours",
                ),
                FieldDefinition(
                    name="location",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Ordre du jour",
            fields=[
                FieldDefinition(
                    name="agenda",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Informations",
            fields=[
                FieldDefinition(
                    name="notes",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="comments",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.FULL,
                    checked_label="Active",
                    unchecked_label="Inactive",
                ),
            ],
        ),
    ],
    collections=[
        FormCollectionDefinition(
            name="internal",
            title="Participants internes",
            description=(
                "Utilisateurs disposant d'un compte Easy Projet."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="participant",
                    label="Participant",
                    field_name="participant",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un participant",
            delete_label="Supprimer le participant",
        ),
        FormCollectionDefinition(
            name="external",
            title="Participants externes",
            description=(
                "Personnes ne disposant pas d'un compte Easy Projet."
            ),
            columns=(
                FormCollectionColumnDefinition(
                    name="external_email",
                    label="Adresse email",
                    field_name="external_email",
                ),
            ),
            allow_add=True,
            allow_delete=True,
            add_label="Ajouter un participant externe",
            delete_label="Supprimer le participant externe",
        ),
    ],
)