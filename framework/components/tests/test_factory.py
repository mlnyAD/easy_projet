

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.components.base.component import EPComponent
from framework.components.factory import ComponentFactory
from framework.components.inputs.text import EPTextInput
from framework.dictionary.entity import EntityDefinition


class ComponentFactoryTests(unittest.TestCase):

    def setUp(self):
        entity = EntityDefinition.from_dictionary(COMPANY_DICTIONARY)
        self.name_field = entity.fields["name"]

    def test_returns_text_input_for_string(self):
        component = ComponentFactory.create(self.name_field)

        self.assertIsInstance(component, EPTextInput)

    def test_component_keeps_field(self):
        component = ComponentFactory.create(self.name_field)

        self.assertIs(component.field, self.name_field)

    def test_component_keeps_name(self):
        component = ComponentFactory.create(self.name_field)

        self.assertEqual(component.name, "name")

    def test_component_keeps_data_type(self):
        component = ComponentFactory.create(self.name_field)

        self.assertEqual(component.data_type, "string")


if __name__ == "__main__":
    unittest.main()