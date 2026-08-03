

import unittest

from framework.button import (
    ButtonAction,
    ButtonDefinition,
    ButtonValidationError,
    ButtonValidator,
)


class ButtonValidatorTests(unittest.TestCase):

    def setUp(self):
        self.validator = ButtonValidator()

    def make_definition(self):

        return ButtonDefinition(
            label="Enregistrer",
            action=ButtonAction.EXECUTE,
        )

    def test_valid_definition_is_accepted(self):

        self.validator.validate(
            self.make_definition(),
        )

    def test_empty_label_is_rejected(self):

        with self.assertRaises(ButtonValidationError):

            self.validator.validate(

                ButtonDefinition(
                    label="",
                )

            )

    def test_invalid_action_is_rejected(self):

        definition = self.make_definition()

        object.__setattr__(
            definition,
            "action",
            "execute",
        )

        with self.assertRaises(ButtonValidationError):

            self.validator.validate(
                definition,
            )

    def test_invalid_disabled_is_rejected(self):

        definition = self.make_definition()

        object.__setattr__(
            definition,
            "disabled",
            "yes",
        )

        with self.assertRaises(ButtonValidationError):

            self.validator.validate(
                definition,
            )


if __name__ == "__main__":
    unittest.main()