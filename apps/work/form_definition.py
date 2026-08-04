

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


WORK_PACKAGE_FORM_DEFINITION = FormDefinition(
    name="work_package",
    title="Lot de travaux",
    sections=[
        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="project",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="code",
                ),
                FieldDefinition(
                    name="name",
                ),
                FieldDefinition(
                    name="description",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Pilotage",
            fields=[
                FieldDefinition(
                    name="status",
                ),
                FieldDefinition(
                    name="manager",
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
            title="Planning",
            fields=[
                FieldDefinition(
                    name="start_date",
                ),
                FieldDefinition(
                    name="end_date",
                ),
                FieldDefinition(
                    name="planned_workload_hours",
                ),
            ],
        ),
    ],
)