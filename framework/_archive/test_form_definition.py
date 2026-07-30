

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.dictionary.entity import EntityDefinition
from framework._archive.form_definition import FormDefinition


class FormDefinitionTests(unittest.TestCase):
    """Tests unitaires de FormDefinition."""

    def setUp(self) -> None:
        self.entity = EntityDefinition.from_dictionary(
            COMPANY_DICTIONARY
        )

    def test_from_entity_returns_form_definition(self) -> None:
        form = FormDefinition.from_entity(self.entity)

        self.assertIsInstance(form, FormDefinition)

    def test_keeps_entity(self) -> None:
        form = FormDefinition.from_entity(self.entity)

        self.assertIs(form.entity, self.entity)

    def test_contains_same_number_of_fields(self) -> None:
        form = FormDefinition.from_entity(self.entity)

        self.assertEqual(
            len(form.fields),
            len(self.entity.fields),
        )

    def test_preserves_field_order(self) -> None:
        form = FormDefinition.from_entity(self.entity)

        self.assertEqual(
            [field.name for field in form.fields],
            list(self.entity.fields.keys()),
        )


if __name__ == "__main__":
    unittest.main()