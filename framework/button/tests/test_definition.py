

import unittest

from framework.button import (
    ButtonAction,
    ButtonDefinition,
    ButtonType,
)


class ButtonDefinitionTests(unittest.TestCase):

    def test_default_values(self):

        definition = ButtonDefinition(
            label="Enregistrer",
        )

        self.assertEqual(
            definition.label,
            "Enregistrer",
        )

        self.assertEqual(
            definition.action,
            ButtonAction.EXECUTE,
        )

        self.assertEqual(
            definition.button_type,
            ButtonType.BUTTON,
        )

        self.assertFalse(
            definition.disabled,
        )

        self.assertIsNone(
            definition.url,
        )

        self.assertIsNone(
            definition.icon,
        )

        self.assertIsNone(
            definition.confirm,
        )

    def test_custom_values(self):

        definition = ButtonDefinition(
            label="Annuler",
            action=ButtonAction.CANCEL,
            button_type=ButtonType.BUTTON,
            url="/companies/",
            icon="x",
            disabled=True,
            confirm="Abandonner ?",
        )

        self.assertEqual(
            definition.action,
            ButtonAction.CANCEL,
        )

        self.assertEqual(
            definition.url,
            "/companies/",
        )

        self.assertEqual(
            definition.icon,
            "x",
        )

        self.assertTrue(
            definition.disabled,
        )

        self.assertEqual(
            definition.confirm,
            "Abandonner ?",
        )


if __name__ == "__main__":
    unittest.main()