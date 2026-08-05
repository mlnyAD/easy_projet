

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


TASK_FORM_DEFINITION = FormDefinition(
    name="task",
    title="Tâche",
    sections=[
        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="work_package",
                    width=FieldWidth.FULL,
                ),
                FieldDefinition(
                    name="status",
                ),
            ],
        ),
        SectionDefinition(
            title="Identification",
            fields=[
                FieldDefinition(
                    name="name",
                ),
                FieldDefinition(
                    name="description",
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
        SectionDefinition(
            title="Planning",
            fields=[
                FieldDefinition(
                    name="planned_start_date",
                ),
                FieldDefinition(
                    name="planned_end_date",
                ),
                FieldDefinition(
                    name="updated_start_date",
                ),
                FieldDefinition(
                    name="updated_end_date",
                ),
                FieldDefinition(
                    name="planned_workload_hours",
                ),
                FieldDefinition(
                    name="remaining_workload_hours",
                ),
                FieldDefinition(
                    name="progress_percent",
                ),
            ],
        ),
    ],
)