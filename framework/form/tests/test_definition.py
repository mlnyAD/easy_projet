

from unittest import TestCase

from framework.form import (
    FieldDefinition,
    FormCollectionDefinition,
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

    def test_create_form_definition_with_collection(self):
        collection = FormCollectionDefinition(
            name="participants",
            title="Participants",
        )

        definition = FormDefinition(
            name="meeting",
            title="Réunion",
            collections=[
                collection,
            ],
        )

        self.assertEqual(
            len(definition.collections),
            1,
        )

        self.assertIs(
            definition.collections[0],
            collection,
        )

    def test_get_existing_collection(self):
        collection = FormCollectionDefinition(
            name="assignments",
            title="Personnel affecté",
        )

        definition = FormDefinition(
            name="task",
            title="Tâche",
            collections=[
                collection,
            ],
        )

        self.assertIs(
            definition.get_collection(
                "assignments"
            ),
            collection,
        )

    def test_get_unknown_collection(self):
        definition = FormDefinition(
            name="task",
            title="Tâche",
        )

        self.assertIsNone(
            definition.get_collection(
                "unknown"
            )
        )