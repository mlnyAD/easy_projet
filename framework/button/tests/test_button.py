

import unittest

from framework.button import (
    ButtonAction,
    ButtonDefinition,
    ButtonType,
    EPButton,
)


class EPButtonTests(unittest.TestCase):

    def test_exposes_definition_properties(self):
        definition = ButtonDefinition(
            label="Enregistrer",
            action=ButtonAction.EXECUTE,
            button_type=ButtonType.SUBMIT,
            icon="save",
        )

        button = EPButton(
            definition=definition,
        )

        self.assertEqual(button.label, "Enregistrer")
        self.assertEqual(button.action, ButtonAction.EXECUTE)
        self.assertEqual(button.button_type, ButtonType.SUBMIT)
        self.assertEqual(button.icon, "save")
        self.assertFalse(button.disabled)
        self.assertIsNone(button.url)
        self.assertIsNone(button.confirm)
        self.assertFalse(button.is_link)

    def test_is_link_when_url_is_defined(self):
        button = EPButton(
            definition=ButtonDefinition(
                label="Annuler",
                action=ButtonAction.CANCEL,
                url="/companies/",
            ),
        )

        self.assertTrue(button.is_link)

    def test_invalid_definition_is_rejected(self):
        with self.assertRaises(TypeError):
            EPButton(
                definition="invalid",
            )


if __name__ == "__main__":
    unittest.main()