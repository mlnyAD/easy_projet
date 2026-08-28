

from unittest import TestCase

from framework.form import (
    FieldDefinition,
    FormDefinition,
    FormValidationError,
    FormValidator,
    SectionDefinition,
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
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
            
    def test_valid_collection_is_accepted(self):
        definition = self.make_valid_definition()

        definition = FormDefinition(
            name=definition.name,
            title=definition.title,
            sections=definition.sections,
            collections=[
                FormCollectionDefinition(
                    name="participants",
                    title="Participants",
                    columns=(
                        FormCollectionColumnDefinition(
                            name="user",
                            label="Utilisateur",
                            field_name="user",
                        ),
                    ),
                ),
            ],
        )

        self.validator.validate(definition)


    def test_collection_without_column_is_rejected(self):
        definition = FormDefinition(
            name="meeting",
            title="Réunion",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
            collections=[
                FormCollectionDefinition(
                    name="participants",
                    title="Participants",
                ),
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)


    def test_duplicate_collection_name_is_rejected(self):
        collection = FormCollectionDefinition(
            name="participants",
            title="Participants",
            columns=(
                FormCollectionColumnDefinition(
                    name="user",
                    field_name="user",
                ),
            ),
        )

        definition = FormDefinition(
            name="meeting",
            title="Réunion",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
            collections=[
                collection,
                collection,
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)


    def test_collection_column_requires_source(self):
        definition = FormDefinition(
            name="task",
            title="Tâche",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
            collections=[
                FormCollectionDefinition(
                    name="assignments",
                    title="Personnel",
                    columns=(
                        FormCollectionColumnDefinition(
                            name="role",
                        ),
                    ),
                ),
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)


    def test_collection_column_cannot_define_two_sources(self):
        definition = FormDefinition(
            name="task",
            title="Tâche",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
            collections=[
                FormCollectionDefinition(
                    name="assignments",
                    title="Personnel",
                    columns=(
                        FormCollectionColumnDefinition(
                            name="role",
                            field_name="role",
                            source_name="user.role",
                        ),
                    ),
                ),
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)


    def test_invalid_collection_alignment_is_rejected(self):
        definition = FormDefinition(
            name="task",
            title="Tâche",
            sections=[
                SectionDefinition(
                    title="Informations",
                    fields=[
                        FieldDefinition("name"),
                    ],
                )
            ],
            collections=[
                FormCollectionDefinition(
                    name="assignments",
                    title="Personnel",
                    columns=(
                        FormCollectionColumnDefinition(
                            name="role",
                            field_name="role",
                            align="invalid",
                        ),
                    ),
                ),
            ],
        )

        with self.assertRaises(FormValidationError):
            self.validator.validate(definition)