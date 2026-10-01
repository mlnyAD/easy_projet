

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
                    width=FieldWidth.MD,
                ),
            ],
        ),
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="code",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="name",
                    width=FieldWidth.MD,
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
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="manager",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    width=FieldWidth.XS,
                    checked_label="Actif",
                    unchecked_label="Inactif",
                ),
            ],
        ),
        SectionDefinition(
            title="Planning",
            fields=[
                FieldDefinition(
                    name="initial_start_date",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="initial_end_date",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="start_date",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="end_date",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="planned_workload_hours",
                    width=FieldWidth.XS,
                ),
            ],
        ),
    ],
)