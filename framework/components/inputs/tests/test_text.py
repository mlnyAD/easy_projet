

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.components.inputs.text import EPTextInput
from framework.dictionary.entity import EntityDefinition


class EPTextInputTests(unittest.TestCase):
    """Tests unitaires de EPTextInput."""

    def setUp(self) -> None:
        entity = EntityDefinition.from_dictionary(
            COMPANY_DICTIONARY
        )
        self.field = entity.fields["name"]

    def test_create_text_input(self) -> None:
        component = EPTextInput(self.field)

        self.assertIsInstance(component, EPTextInput)

    def test_keeps_field_definition(self) -> None:
        component = EPTextInput(self.field)

        self.assertIs(component.field, self.field)

    def test_exposes_field_name(self) -> None:
        component = EPTextInput(self.field)

        self.assertEqual(component.name, "name")

    def test_exposes_data_type(self) -> None:
        component = EPTextInput(self.field)

        self.assertEqual(component.data_type, "string")


if __name__ == "__main__":
    unittest.main()