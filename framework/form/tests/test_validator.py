

from unittest import TestCase

from framework.form import (
    FieldDefinition,
    FormDefinition,
    FormValidationError,
    FormValidator,
    SectionDefinition,
)


class FormValidatorTests(TestCase):
    def setUp(self):
        self.validator = FormValidator()

    def make_valid_definition(self):
        return FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations générales",
                    fields=[
                        FieldDefinition("name"),
                        FieldDefinition("email"),
                    ],
                )
            ],
        )

    def test_valid_definition_is_accepted(self):
        self.validator.validate(
            self.make_valid_definition()
        )

    def test_invalid_definition_type_is_rejected(self):
        with self.assertRaises(FormValidationError):
            self.validator.validate({})

    def test_empty_form_name_is_rejected(self):
        definition = FormDefinition(
            name=" ",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_empty_form_title_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title=" ",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_form_without_section_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_empty_section_title_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title=" ",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_section_without_field_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations",
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_empty_field_name_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition(" "),
                    ],
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_duplicate_field_name_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations générales",
                    fields=[
                        FieldDefinition("name"),
                    ],
                ),
                SectionDefinition(
                    title="Compléments",
                    fields=[
                        FieldDefinition("name"),
                    ],
                ),
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)

    def test_readonly_and_disabled_field_is_rejected(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition(
                            "name",
                            readonly=True,
                            disabled=True,
                        ),
                    ],
                )
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)