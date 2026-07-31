

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)


COMPANY_FORM_DEFINITION = FormDefinition(
    name="company",
    title="Société",
    sections=[
        SectionDefinition(
            title="Informations générales",
            fields=[
                FieldDefinition(name="name"),
                FieldDefinition(name="siret"),
                FieldDefinition(name="vat_number"),
                FieldDefinition(name="is_active"),
            ],
        ),
        SectionDefinition(
            title="Coordonnées",
            fields=[
                FieldDefinition(name="email"),
                FieldDefinition(name="phone"),
            ],
        ),
        SectionDefinition(
            title="Adresse",
            fields=[
                FieldDefinition(name="address_1"),
                FieldDefinition(name="address_2"),
                FieldDefinition(name="address_3"),
                FieldDefinition(name="postal_code"),
                FieldDefinition(name="city"),
                FieldDefinition(name="country"),
            ],
        ),
    ],
)