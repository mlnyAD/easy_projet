

from unittest import TestCase

from framework.form import (
    FieldDefinition,
    FormDefinition,
    SectionDefinition,
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