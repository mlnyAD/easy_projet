

import unittest

from framework.providers.definition import ChoiceProviderDefinition


class ChoiceProviderDefinitionTestCase(unittest.TestCase):
    """Tests de ChoiceProviderDefinition."""

    def test_create_definition(self):
        definition = ChoiceProviderDefinition(
            provider="catalog",
            source="COMPANY_TYPE",
        )

        self.assertEqual(
            definition.provider,
            "catalog",
        )

        self.assertEqual(
            definition.source,
            "COMPANY_TYPE",
        )

    def test_source_is_optional(self):
        definition = ChoiceProviderDefinition(
            provider="company",
        )

        self.assertEqual(
            definition.provider,
            "company",
        )

        self.assertIsNone(
            definition.source,
        )

    def test_definition_is_immutable(self):
        definition = ChoiceProviderDefinition(
            provider="catalog",
        )

        with self.assertRaises(Exception):
            definition.provider = "company"


if __name__ == "__main__":
    unittest.main()