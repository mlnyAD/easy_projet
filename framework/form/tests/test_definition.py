

from unittest import TestCase

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
)
from framework.defaults.field import (
    DEFAULT_FIELD_CHECKED_LABEL,
    DEFAULT_FIELD_UNCHECKED_LABEL,
)


class FormDefinitionTests(TestCase):
    def test_create_form_definition(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                        FieldDefinition("email"),
                    ],
                )
            ],
        )

        self.assertEqual(
            definition.name,
            "company",
        )

        self.assertEqual(
            len(definition.sections),
            1,
        )

        self.assertEqual(
            len(definition.sections[0].fields),
            2,
        )

    def test_field_name(self):
        field = FieldDefinition("name")

        self.assertEqual(
            field.name,
            "name",
        )

        self.assertTrue(
            field.required,
        )

    def test_section_title(self):
        section = SectionDefinition(
            title="Adresse",
        )

        self.assertEqual(
            section.title,
            "Adresse",
        )
    
    def test_get_existing_field(self):
        field = FieldDefinition(name="name")

        definition = FormDefinition(
            name="company",
            title="Company",
            sections=[
                SectionDefinition(
                    title="General",
                    fields=[field],
                ),
            ],
        )

        self.assertIs(
            definition.get_field("name"),
            field,
        )
        
    def test_get_unknown_field(self):
        definition = FormDefinition(
            name="company",
            title="Company",
            sections=[
                SectionDefinition(
                    title="General",
                    fields=[
                        FieldDefinition(name="name"),
                    ],
                ),
            ],
        )

        self.assertIsNone(
            definition.get_field("unknown"),
        )        

    def test_get_field_in_second_section(self):
        field = FieldDefinition(name="city")

        definition = FormDefinition(
            name="company",
            title="Company",
            sections=[
                SectionDefinition(
                    title="General",
                    fields=[
                        FieldDefinition(name="name"),
                    ],
                ),
                SectionDefinition(
                    title="Address",
                    fields=[field],
                ),
            ],
        )

        self.assertIs(
            definition.get_field("city"),
            field,
        )
        
    def test_boolean_labels_use_framework_defaults(self):
        field = FieldDefinition(name="is_active")

        self.assertEqual(
            field.checked_label,
            DEFAULT_FIELD_CHECKED_LABEL,
        )
        self.assertEqual(
            field.unchecked_label,
            DEFAULT_FIELD_UNCHECKED_LABEL,
        )

    def test_boolean_labels_can_be_overridden(self):
        field = FieldDefinition(
            name="is_active",
            checked_label="Actif",
            unchecked_label="Inactif",
        )

        self.assertEqual(field.checked_label, "Actif")
        self.assertEqual(field.unchecked_label, "Inactif")