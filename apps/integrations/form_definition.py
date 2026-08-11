

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.types.field_width import FieldWidth


EXTERNAL_INTEGRATION_FORM_DEFINITION = FormDefinition(
    name="external_integration",
    title="Intégration externe",
    sections=[
        SectionDefinition(
            title="Rattachement",
            fields=[
                FieldDefinition(
                    name="client_environment",
                    width=FieldWidth.FULL,
                ),
            ],
        ),
        SectionDefinition(
            title="Service",
            fields=[
                FieldDefinition(
                    name="service_type",
                ),
                FieldDefinition(
                    name="provider",
                ),
                FieldDefinition(
                    name="connection_status",
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
            ],
        ),
        SectionDefinition(
            title="Orchestration",
            fields=[
                FieldDefinition(
                    name="priority",
                ),
                FieldDefinition(
                    name="is_active",
                    required=False,
                    checked_label="Active",
                    unchecked_label="Inactive",
                ),
            ],
        ),
    ],
)