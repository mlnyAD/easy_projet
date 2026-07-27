

import unittest

from framework.context import EPContext
from framework.form import (
    EPForm,
    FieldDefinition,
    FieldKind,
    FormDefinition,
    SectionDefinition,
)
from framework.providers import ProviderRegistry
from framework.providers import (
    Choice,
    ChoiceProvider,
    ChoiceProviderDefinition,
    ProviderRegistry,
)


class EPFormTestCase(unittest.TestCase):

    def test_create_form(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations générales",
                    fields=[
                        FieldDefinition(
                            name="name",
                            label="Nom",
                        ),
                    ],
                ),
            ],
        )

        context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        providers = ProviderRegistry()

        form = EPForm(
            definition=definition,
            context=context,
            providers=providers,
        )

        self.assertIs(form.definition, definition)
        self.assertIs(form.context, context)
        self.assertIs(form.providers, providers)

    def test_title_returns_definition_title(self):
        definition = FormDefinition(
            name="company",
            title="Société",
        )

        form = EPForm(
            definition=definition,
            context=EPContext(
                operator="operator",
                client_environment="environment",
            ),
            providers=ProviderRegistry(),
        )

        self.assertEqual(
            form.title,
            "Société",
        )

    def test_sections_returns_definition_sections(self):
        definition = FormDefinition(
            name="company",
            title="Société",
        )

        form = EPForm(
            definition=definition,
            context=EPContext(
                operator="operator",
                client_environment="environment",
            ),
            providers=ProviderRegistry(),
        )

        self.assertIs(
            form.sections,
            definition.sections,
        )
        
if __name__ == "__main__":
    unittest.main()
    
class DummyChoiceProvider(ChoiceProvider):

    def __init__(self):
        self.definition = None
        self.context = None

    def get_choices(
        self,
        definition,
        context,
    ):
        self.definition = definition
        self.context = context

        return [
            Choice(
                value="FR",
                label="France",
            ),
        ]
        
    def test_get_choices_without_provider(self):
        field = FieldDefinition(
            name="country",
            kind=FieldKind.SELECT,
        )

        form = EPForm(
            definition=self.definition,
            context=self.context,
            providers=ProviderRegistry(),
        )

        self.assertEqual(
            form.get_choices(field),
            [],
        )

    def test_get_choices_calls_provider(self):
        provider = DummyChoiceProvider()

        registry = ProviderRegistry()
        registry.register(
            "catalog",
            provider,
        )

        field = FieldDefinition(
            name="country",
            kind=FieldKind.SELECT,
            provider=ChoiceProviderDefinition(
                provider="catalog",
                source="country",
            ),
        )

        form = EPForm(
            definition=self.definition,
            context=self.context,
            providers=registry,
        )

        form.get_choices(field)

        self.assertIs(
            provider.definition,
            field.provider,
        )

        self.assertIs(
            provider.context,
            self.context,
        )        
        
    def test_get_choices_returns_choices(self):
        provider = DummyChoiceProvider()

        registry = ProviderRegistry()
        registry.register(
            "catalog",
            provider,
        )

        field = FieldDefinition(
            name="country",
            kind=FieldKind.SELECT,
            provider=ChoiceProviderDefinition(
                provider="catalog",
                source="country",
            ),
        )

        form = EPForm(
            definition=self.definition,
            context=self.context,
            providers=registry,
        )

        self.assertEqual(
            form.get_choices(field),
            [
                Choice(
                    value="FR",
                    label="France",
                ),
            ],
        )