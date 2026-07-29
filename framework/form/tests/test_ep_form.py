

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.components.inputs.text import EPTextInput
from framework.dictionary.entity import EntityDefinition
from framework.form.ep_form import EPForm
from framework.form.form_definition import FormDefinition


class EPFormTests(unittest.TestCase):

    def setUp(self):
        entity = EntityDefinition.from_dictionary(COMPANY_DICTIONARY)
        self.definition = FormDefinition.from_entity(entity)
        self.form = EPForm(self.definition)

    def test_create_ep_form(self):
        self.assertIsInstance(self.form, EPForm)

    def test_keeps_definition(self):
        self.assertIs(self.form.definition, self.definition)

    def test_exposes_entity(self):
        self.assertIs(
            self.form.entity,
            self.definition.entity,
        )

    def test_preserves_field_order(self):
        self.assertEqual(
            [field.name for field in self.form.fields],
            [field.name for field in self.definition.fields],
        )

    def test_components_count(self):
        self.assertEqual(
            len(self.form.components),
            len(self.form.fields),
        )

    def test_name_component_is_text_input(self):
        component = next(
            component
            for component in self.form.components
            if component.name == "name"
        )

        self.assertIsInstance(component, EPTextInput)

    def test_name_component_keeps_field_name(self):
        component = next(
            component
            for component in self.form.components
            if component.name == "name"
        )

        self.assertEqual(component.name, "name")

if __name__ == "__main__":
    unittest.main()