

import os
import unittest
from unittest.mock import patch

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from django.http import HttpRequest, HttpResponse

from framework.context import EPContext
from framework.form import (
    EPForm,
    FormDefinition,
)
from framework.integrations.django import (
    DEFAULT_FORM_TEMPLATE_NAME,
    FORM_VIEW_CONTEXT_KEY,
    DjangoFormRenderer,
)
from framework.providers import ProviderRegistry
from framework.form import (
    FieldDefinition,
    FieldKind,
    FormDefinition,
    SectionDefinition,
    EPForm,
)

class DjangoFormRendererTests(unittest.TestCase):

    def setUp(self) -> None:
        self.request = HttpRequest()

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
        )

        self.renderer = DjangoFormRenderer()

    def test_default_template_name(self) -> None:
        self.assertEqual(
            self.renderer.template_name,
            DEFAULT_FORM_TEMPLATE_NAME,
        )

    def test_custom_template_name(self) -> None:
        renderer = DjangoFormRenderer(
            template_name="custom/form.html",
        )

        self.assertEqual(
            renderer.template_name,
            "custom/form.html",
        )

    def test_template_name_is_normalized(self) -> None:
        renderer = DjangoFormRenderer(
            template_name="  custom/form.html  ",
        )

        self.assertEqual(
            renderer.template_name,
            "custom/form.html",
        )

    def test_invalid_template_name_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            DjangoFormRenderer(
                template_name=123,
            )

    def test_empty_template_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DjangoFormRenderer(
                template_name="   ",
            )

    def test_invalid_request_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request="request",
                form=self.form,
            )

    def test_invalid_form_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                form="form",
            )

    def test_invalid_context_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                form=self.form,
                context=["invalid"],
            )

    def test_reserved_context_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.renderer.render(
                request=self.request,
                form=self.form,
                context={
                    FORM_VIEW_CONTEXT_KEY: "invalid",
                },
            )

    def test_build_context_contains_form(self) -> None:
        context = self.renderer._build_context(
            form=self.form,
            context=None,
        )

        self.assertEqual(
            context,
            {
                FORM_VIEW_CONTEXT_KEY: self.form,
            },
        )

    def test_build_context_merges_additional_context(self) -> None:
        context = self.renderer._build_context(
            form=self.form,
            context={
                "page_title": "Société",
            },
        )

        self.assertEqual(
            context,
            {
                "page_title": "Société",
                FORM_VIEW_CONTEXT_KEY: self.form,
            },
        )

    def test_invalid_status_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                form=self.form,
                status="200",
            )

    def test_invalid_status_value_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.renderer.render(
                request=self.request,
                form=self.form,
                status=99,
            )

    @patch(
        "framework.integrations.django.form_renderer.django_render"
    )
    def test_render_uses_default_template(
        self,
        django_render_mock,
    ) -> None:
        expected_response = HttpResponse("content")
        django_render_mock.return_value = expected_response

        response = self.renderer.render(
            request=self.request,
            form=self.form,
        )

        self.assertIs(
            response,
            expected_response,
        )

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name=DEFAULT_FORM_TEMPLATE_NAME,
            context={
                FORM_VIEW_CONTEXT_KEY: self.form,
            },
            status=None,
        )

    @patch(
        "framework.integrations.django.form_renderer.django_render"
    )
    def test_render_uses_temporary_template(
        self,
        django_render_mock,
    ) -> None:
        django_render_mock.return_value = HttpResponse()

        self.renderer.render(
            request=self.request,
            form=self.form,
            template_name="custom/form.html",
        )

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name="custom/form.html",
            context={
                FORM_VIEW_CONTEXT_KEY: self.form,
            },
            status=None,
        )

    @patch(
        "framework.integrations.django.form_renderer."
        "django_render_to_string"
    )
    def test_render_to_string_returns_html(
        self,
        django_render_to_string_mock,
    ) -> None:
        django_render_to_string_mock.return_value = (
            "<form></form>"
        )

        html = self.renderer.render_to_string(
            request=self.request,
            form=self.form,
        )

        self.assertEqual(
            html,
            "<form></form>",
        )

        django_render_to_string_mock.assert_called_once_with(
            template_name=DEFAULT_FORM_TEMPLATE_NAME,
            context={
                FORM_VIEW_CONTEXT_KEY: self.form,
            },
            request=self.request,
        )

    def test_render_to_string_invalid_request(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render_to_string(
                request="request",
                form=self.form,
            )

    def test_render_to_string_invalid_form(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render_to_string(
                request=self.request,
                form="form",
            )

    def test_real_render_returns_http_response(self) -> None:
        response = self.renderer.render(
            request=self.request,
            form=self.form,
        )

        self.assertIsInstance(
            response,
            HttpResponse,
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        
    def test_real_render_to_string_returns_html(self) -> None:
        html = self.renderer.render_to_string(
            request=self.request,
            form=self.form,
        )

        self.assertIsInstance(
            html,
            str,
        )

        self.assertGreater(
            len(html),
            0,
        )
        
    def test_render_to_string_renders_text_field(self) -> None:
        form = EPForm(
            definition=FormDefinition(
                name="company",
                title="Société",
                sections=[
                    SectionDefinition(
                        title="Informations générales",
                        fields=[
                            FieldDefinition(
                                name="company_name",
                                label="Nom",
                                kind=FieldKind.TEXT,
                            ),
                        ],
                    ),
                ],
            ),
            context=EPContext(
                operator=object(),
                client_environment=object(),
            ),
            providers=ProviderRegistry(),
        )

        html = self.renderer.render_to_string(
            request=self.request,
            form=form,
        )

        self.assertIn("Nom", html)
        self.assertIn('name="company_name"', html)
        self.assertIn('type="text"', html)    
        
if __name__ == "__main__":
    unittest.main()