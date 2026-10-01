

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
                    width=FieldWidth.MD,
                ),
            ],
        ),
        SectionDefinition(
            title="Service",
            fields=[
                FieldDefinition(
                    name="service_type",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="provider",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="connection_status",
                    width=FieldWidth.XS,
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
                    width=FieldWidth.XS,
                ),
            ],
        ),
        SectionDefinition(
            title="Orchestration",
            fields=[
                FieldDefinition(
                    name="priority",
                    width=FieldWidth.XS,
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