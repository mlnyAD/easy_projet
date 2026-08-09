

from framework.form import (
    FieldDefinition,
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
)