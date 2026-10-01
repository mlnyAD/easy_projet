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
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="subject",
                    width=FieldWidth.MD,
                ),
                FieldDefinition(
                    name="organizer",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="status",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="reference",
                    width=FieldWidth.XS,
                ),
            ],
        ),
        SectionDefinition(
            title="Organisation",
            fields=[
                FieldDefinition(
                    name="scheduled_at",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="duration_hours",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="location",
                    width=FieldWidth.MD,
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
                "Utilisateurs actifs rattachés au projet."
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
                "Personnes sans accès au projet, invitées par email."
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
