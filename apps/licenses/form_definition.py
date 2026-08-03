

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)


LICENSE_FORM_DEFINITION = FormDefinition(
    name="license",
    title="Licence",
    sections=[
        SectionDefinition(
            title="Attribution",
            fields=[
                FieldDefinition(name="company"),
                FieldDefinition(name="reference"),
                FieldDefinition(name="project_capacity"),
            ],
        ),
        SectionDefinition(
            title="Validité",
            fields=[
                FieldDefinition(name="granted_at"),
                FieldDefinition(name="expiration_date"),
            ],
        ),
    ],
)