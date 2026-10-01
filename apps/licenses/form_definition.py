

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)

from framework.types.field_width import FieldWidth

LICENSE_FORM_DEFINITION = FormDefinition(
    name="license",
    title="Licence",
    sections=[
        SectionDefinition(
            title="Attribution",
            fields=[
                FieldDefinition(
                    name="company",
                    width=FieldWidth.SM,
                ),
                FieldDefinition(
                    name="reference",
                    width=FieldWidth.SM,
                   ),
                FieldDefinition(
                    name="project_capacity",
                    width=FieldWidth.XS,
                ),
            ],
        ),
        SectionDefinition(
            title="Validité",
            fields=[
                FieldDefinition(
                    name="granted_at",
                    width=FieldWidth.XS,
                ),
                FieldDefinition(
                    name="expiration_date",
                    width=FieldWidth.XS,
                ),
            ],
        ),
    ],
)