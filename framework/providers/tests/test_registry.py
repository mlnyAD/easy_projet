

import unittest

from framework.context import EPContext
from framework.providers.provider import ChoiceProvider
from framework.providers.registry import ProviderRegistry


class DummyProvider(ChoiceProvider):

    def get_choices(
        self,
        definition,
        context: EPContext,
    ) -> list:
        return []


class ProviderRegistryTestCase(unittest.TestCase):

    def test_register_provider(self):
        registry = ProviderRegistry()

        provider = DummyProvider()

        registry.register(
            "dummy",
            provider,
        )

        self.assertIs(
            registry.get("dummy"),
            provider,
        )

    def test_unknown_provider(self):
        registry = ProviderRegistry()

        with self.assertRaises(KeyError):
            registry.get("unknown")

    def test_register_overwrites_provider(self):
        registry = ProviderRegistry()

        provider1 = DummyProvider()
        provider2 = DummyProvider()

        registry.register("dummy", provider1)
        registry.register("dummy", provider2)

        self.assertIs(
            registry.get("dummy"),
            provider2,
        )


if __name__ == "__main__":
    unittest.main()