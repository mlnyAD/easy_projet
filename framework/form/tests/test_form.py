

import unittest

from django import forms

from framework.context import EPContext
from framework.form import (
    EPForm,
    FieldDefinition,
    FieldKind,
    FormDefinition,
    SectionDefinition,
)
from framework.form.resolved_section import ResolvedSection
from framework.providers import (
    Choice,
    ChoiceProvider,
    ChoiceProviderDefinition,
    ProviderRegistry,
)


class DummyForm(forms.Form):
    """
    Formulaire Django minimal utilisé par les tests.
    """

    name = forms.CharField(required=False)
    country = forms.ChoiceField(required=False)


class DummyChoiceProvider(ChoiceProvider):
    """
    Fournisseur de choix factice utilisé par les tests.
    """

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


class EPFormTestCase(unittest.TestCase):

    def setUp(self):
        self.context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        self.providers = ProviderRegistry()

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

        django_form = DummyForm()

        form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=django_form,
        )

        self.assertIs(form.definition, definition)
        self.assertIs(form.context, self.context)
        self.assertIs(form.providers, self.providers)
        self.assertIs(form.django_form, django_form)

    def test_title_returns_definition_title(self):
        definition = FormDefinition(
            name="company",
            title="Société",
        )

        form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=DummyForm(),
        )

        self.assertEqual(
            form.title,
            "Société",
        )

    def test_sections_returns_resolved_sections(self):
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

        django_form = DummyForm()

        form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=django_form,
        )

        sections = form.sections

        self.assertEqual(len(sections), 1)
        self.assertIsInstance(sections[0], ResolvedSection)
        self.assertEqual(
            sections[0].title,
            "Informations générales",
        )
        self.assertEqual(len(sections[0].fields), 1)
        resolved_field = sections[0].fields[0]

        self.assertEqual(
            resolved_field.bound_field.name,
            "name",
        )

        self.assertIs(
            resolved_field.bound_field.form,
            django_form,
        )

    def test_sections_raises_error_when_field_does_not_exist(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations générales",
                    fields=[
                        FieldDefinition(
                            name="unknown_field",
                        ),
                    ],
                ),
            ],
        )

        form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=DummyForm(),
        )

        with self.assertRaisesRegex(
            ValueError,
            "unknown_field",
        ):
            _ = form.sections

    def test_get_choices_without_provider(self):
        field = FieldDefinition(
            name="country",
            kind=FieldKind.SELECT,
        )

        form = EPForm(
            definition=FormDefinition(
                name="company",
                title="Société",
            ),
            context=self.context,
            providers=self.providers,
            django_form=DummyForm(),
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
            definition=FormDefinition(
                name="company",
                title="Société",
            ),
            context=self.context,
            providers=registry,
            django_form=DummyForm(),
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
            definition=FormDefinition(
                name="company",
                title="Société",
            ),
            context=self.context,
            providers=registry,
            django_form=DummyForm(),
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


if __name__ == "__main__":
    unittest.main()