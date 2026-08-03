

import os
import unittest

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from django import forms

from framework.context import EPContext
from framework.form import (
    EPForm,
    FormDefinition,
)
from framework.integrations.django import (
    DjangoFormRenderer,
    FORM_VIEW_CONTEXT_KEY,
)
from framework.providers import ProviderRegistry
from framework.viewmodel import FormViewModel


class EmptyDjangoForm(forms.Form):
    """Formulaire Django minimal utilisé par les tests."""


class DjangoFormRendererTests(unittest.TestCase):

    def setUp(self) -> None:
        self.form = EPForm(
            definition=FormDefinition(
                name="company",
                title="Société",
                sections=[],
            ),
            context=EPContext(
                operator=object(),
                client_environment=object(),
            ),
            providers=ProviderRegistry(),
            django_form=EmptyDjangoForm(),
        )

        self.renderer = DjangoFormRenderer()

    def test_build_view_model_returns_form_view_model(
        self,
    ) -> None:
        view_model = self.renderer.build_view_model(
            self.form,
            cancel_url="/companies/",
        )

        self.assertIsInstance(
            view_model,
            FormViewModel,
        )

        self.assertIs(
            view_model.form,
            self.form,
        )

        self.assertEqual(
            view_model.cancel_url,
            "/companies/",
        )

    def test_build_context_contains_form_view(
        self,
    ) -> None:
        context = self.renderer.build_context(
            self.form,
        )

        self.assertIn(
            FORM_VIEW_CONTEXT_KEY,
            context,
        )

        self.assertIsInstance(
            context[FORM_VIEW_CONTEXT_KEY],
            FormViewModel,
        )

    def test_build_context_merges_context(
        self,
    ) -> None:
        context = self.renderer.build_context(
            self.form,
            context={
                "page_title": "Société",
            },
        )

        self.assertEqual(
            context["page_title"],
            "Société",
        )

        self.assertIn(
            FORM_VIEW_CONTEXT_KEY,
            context,
        )

    def test_build_context_with_cancel_url(
        self,
    ) -> None:
        context = self.renderer.build_context(
            self.form,
            cancel_url="/companies/",
        )

        form_view = context[
            FORM_VIEW_CONTEXT_KEY
        ]

        self.assertEqual(
            form_view.cancel_url,
            "/companies/",
        )

    def test_invalid_form_is_rejected(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            self.renderer.build_context(
                "invalid",
            )

    def test_invalid_context_is_rejected(
        self,
    ) -> None:
        with self.assertRaises(TypeError):
            self.renderer.build_context(
                self.form,
                context=["invalid"],
            )

    def test_reserved_context_key_is_rejected(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            self.renderer.build_context(
                self.form,
                context={
                    FORM_VIEW_CONTEXT_KEY: "invalid",
                },
            )


if __name__ == "__main__":
    unittest.main()