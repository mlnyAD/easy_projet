

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.components.base.component import EPComponent
from framework.dictionary.entity import EntityDefinition


class EPComponentTests(unittest.TestCase):
    """Tests unitaires de EPComponent."""

    def setUp(self) -> None:
        entity = EntityDefinition.from_dictionary(
            COMPANY_DICTIONARY
        )
        self.field = entity.fields["name"]

    def test_create_component(self) -> None:
        component = EPComponent(self.field)

        self.assertIsInstance(component, EPComponent)

    def test_keeps_field_definition(self) -> None:
        component = EPComponent(self.field)

        self.assertIs(component.field, self.field)

    def test_exposes_field_name(self) -> None:
        component = EPComponent(self.field)

        self.assertEqual(component.name, "name")


if __name__ == "__main__":
    unittest.main()