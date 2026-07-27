

import unittest

from framework.context import EPContext
from framework.providers.provider import ChoiceProvider
from framework.providers import Choice

class ConcreteChoiceProvider(ChoiceProvider):
    """Provider concret utilisé uniquement par les tests."""

    def get_choices(
        self,
        definition,
        context: EPContext,
    ) -> list[Choice]:
        return [
            Choice(
                value="value_1",
                label="Label 1",
            ),
            Choice(
                value="value_2",
                label="Label 2",
            ),
        ]

class ChoiceProviderTestCase(unittest.TestCase):
    """Tests du contrat ChoiceProvider."""

    def setUp(self):
        self.context = EPContext(
            operator="operator",
            client_environment="environment",
        )

    def test_choice_provider_is_abstract(self):
        """ChoiceProvider ne peut pas être instancié directement."""

        with self.assertRaises(TypeError):
            ChoiceProvider()

    def test_concrete_provider_can_be_created(self):
        """Un provider implémentant get_choices peut être instancié."""

        provider = ConcreteChoiceProvider()

        self.assertIsInstance(provider, ChoiceProvider)

    def test_concrete_provider_returns_choices(self):
        """Le provider concret retourne les choix attendus."""

        provider = ConcreteChoiceProvider()

        choices = provider.get_choices(
            definition="definition",
            context=self.context,
        )

        self.assertEqual(
            choices,
            [
                Choice(
                    value="value_1",
                    label="Label 1",
                ),
                Choice(
                    value="value_2",
                    label="Label 2",
                ),
            ],
        )

if __name__ == "__main__":
    unittest.main()