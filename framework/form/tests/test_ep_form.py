

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.dictionary.entity import EntityDefinition
from framework.form.ep_form import EPForm
from framework.form.form_definition import FormDefinition


class EPFormTests(unittest.TestCase):

    def setUp(self):
        entity = EntityDefinition.from_dictionary(COMPANY_DICTIONARY)
        self.definition = FormDefinition.from_entity(entity)

    def test_create_ep_form(self):
        form = EPForm(self.definition)

        self.assertIsInstance(form, EPForm)

    def test_keeps_definition(self):
        form = EPForm(self.definition)

        self.assertIs(form.definition, self.definition)

    def test_exposes_entity(self):
        form = EPForm(self.definition)

        self.assertIs(
            form.entity,
            self.definition.entity,
        )

    def test_preserves_field_order(self):
        form = EPForm(self.definition)

        self.assertEqual(
            [field.name for field in form.fields],
            [field.name for field in self.definition.fields],
        )


if __name__ == "__main__":
    unittest.main()