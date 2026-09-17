

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
from framework.form.resolved_field import ResolvedField
from django.forms import formset_factory

from framework.form import (
    FormCollectionDefinition,
)

class DummyForm(forms.Form):
    """
    Formulaire Django minimal utilisé par les tests.
    """

    name = forms.CharField(required=False)
    country = forms.ChoiceField(required=False)
    is_active = forms.BooleanField(required=False)


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
        
    def test_resolved_field_exposes_boolean_labels(self):
        definition = FormDefinition(
            name="company",
            title="Société",
            sections=[
                SectionDefinition(
                    title="Informations générales",
                    fields=[
                        FieldDefinition(
                            name="is_active",
                            checked_label="Active",
                            unchecked_label="Inactive",
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

        resolved_field = form.sections[0].fields[0]

        self.assertEqual(
            resolved_field.checked_label,
            "Active",
        )
        self.assertEqual(
            resolved_field.unchecked_label,
            "Inactive",
        )
        
    def test_resolved_field_exposes_catalog_metadata(self):
        django_form = DummyForm()

        bound_field = django_form["country"]
        bound_field.field.catalog_code = "COUNTRY"
        bound_field.field.catalog_is_editable = True
        bound_field.field.catalog_is_incremental = True

        resolved_field = ResolvedField(
            definition=FieldDefinition(name="country"),
            bound_field=bound_field,
        )

        self.assertEqual(
            resolved_field.catalog_code,
            "COUNTRY",
        )
        self.assertTrue(
            resolved_field.catalog_is_editable,
        )
        self.assertTrue(
            resolved_field.catalog_is_incremental,
        )
        self.assertTrue(
            resolved_field.allows_catalog_increment,
        )
    
    def test_resolve_collection(self):
        class ItemForm(forms.Form):
            name = forms.CharField()

        item_formset_class = formset_factory(
            ItemForm,
            extra=1,
            can_delete=True,
        )

        item_formset = item_formset_class(
            prefix="items",
        )

        definition = FormDefinition(
            name="sample",
            title="Exemple",
            collections=[
                FormCollectionDefinition(
                    name="items",
                    title="Éléments",
                ),
            ],
        )

        ep_form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=self.django_form,
            formsets={
                "items": item_formset,
            },
        )

        collections = ep_form.collections

        self.assertEqual(
            len(collections),
            1,
        )

        self.assertEqual(
            collections[0].name,
            "items",
        )

        self.assertIs(
            collections[0].formset,
            item_formset,
        )        
        
    def test_missing_collection_formset_raises_error(self):
        definition = FormDefinition(
            name="sample",
            title="Exemple",
            collections=[
                FormCollectionDefinition(
                    name="items",
                    title="Éléments",
                ),
            ],
        )

        ep_form = EPForm(
            definition=definition,
            context=self.context,
            providers=self.providers,
            django_form=self.django_form,
        )

        with self.assertRaisesRegex(
            ValueError,
            "items",
        ):
            ep_form.collections   
            
    def setUp(self):
        self.context = EPContext(
            operator="operator",
            client_environment="environment",
        )

        self.providers = ProviderRegistry()

        self.django_form = DummyForm()

if __name__ == "__main__":
    unittest.main()