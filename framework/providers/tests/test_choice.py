

from dataclasses import FrozenInstanceError
import unittest

from framework.providers.choice import Choice


class ChoiceTestCase(unittest.TestCase):
    """Tests de Choice."""

    def test_create_choice(self):
        """Un choix est correctement créé."""

        choice = Choice(
            value="A",
            label="Choix A",
        )

        self.assertEqual(choice.value, "A")
        self.assertEqual(choice.label, "Choix A")

    def test_choice_is_immutable(self):
        """Choice est immuable."""

        choice = Choice(
            value="A",
            label="Choix A",
        )

        with self.assertRaises(FrozenInstanceError):
            choice.value = "B"

    def test_choice_uses_slots(self):
        """Choice utilise __slots__."""

        choice = Choice(
            value="A",
            label="Choix A",
        )

        with self.assertRaises(
            (AttributeError, TypeError, FrozenInstanceError)
        ):
            choice.description = "Description"


if __name__ == "__main__":
    unittest.main()