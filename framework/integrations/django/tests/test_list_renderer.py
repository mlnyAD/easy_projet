

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

from framework.integrations.django import (
    DEFAULT_LIST_TEMPLATE_NAME,
    LIST_VIEW_CONTEXT_KEY,
    DjangoListRenderer,
)
from framework.viewmodel import (
    ListViewModel,
    PaginationViewModel,
)


class DjangoListRendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = HttpRequest()

        self.pagination = PaginationViewModel(
            page=1,
            page_size=20,
            total_items=0,
            total_pages=0,
            has_previous=False,
            has_next=False,
            previous_page=None,
            next_page=None,
        )

        self.view_model = ListViewModel(
            columns=(),
            rows=(),
            pagination=self.pagination,
        )

        self.renderer = DjangoListRenderer()

    def test_default_template_name(self) -> None:
        self.assertEqual(
            self.renderer.template_name,
            DEFAULT_LIST_TEMPLATE_NAME,
        )

    def test_custom_template_name(self) -> None:
        renderer = DjangoListRenderer(
            template_name="custom/list.html",
        )

        self.assertEqual(
            renderer.template_name,
            "custom/list.html",
        )

    def test_template_name_is_normalized(self) -> None:
        renderer = DjangoListRenderer(
            template_name="  custom/list.html  ",
        )

        self.assertEqual(
            renderer.template_name,
            "custom/list.html",
        )

    def test_invalid_template_name_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            DjangoListRenderer(
                template_name=123,
            )

    def test_empty_template_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DjangoListRenderer(
                template_name="   ",
            )

    def test_invalid_request_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request="request",
                view_model=self.view_model,
            )

    def test_invalid_view_model_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                view_model="view-model",
            )

    def test_invalid_context_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                view_model=self.view_model,
                context=["invalid"],
            )

    def test_reserved_context_key_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.renderer.render(
                request=self.request,
                view_model=self.view_model,
                context={
                    LIST_VIEW_CONTEXT_KEY: "invalid",
                },
            )

    def test_invalid_status_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.renderer.render(
                request=self.request,
                view_model=self.view_model,
                status="200",
            )

    def test_invalid_status_value_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.renderer.render(
                request=self.request,
                view_model=self.view_model,
                status=99,
            )

    @patch(
        "framework.integrations.django.list_renderer.django_render"
    )
    def test_render_uses_default_template(
        self,
        django_render_mock,
    ) -> None:
        expected_response = HttpResponse("content")
        django_render_mock.return_value = expected_response

        response = self.renderer.render(
            request=self.request,
            view_model=self.view_model,
        )

        self.assertIs(response, expected_response)

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name=DEFAULT_LIST_TEMPLATE_NAME,
            context={
                LIST_VIEW_CONTEXT_KEY: self.view_model,
            },
            status=None,
        )

    @patch(
        "framework.integrations.django.list_renderer.django_render"
    )
    def test_render_uses_temporary_template(
        self,
        django_render_mock,
    ) -> None:
        django_render_mock.return_value = HttpResponse()

        self.renderer.render(
            request=self.request,
            view_model=self.view_model,
            template_name="temporary/list.html",
        )

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name="temporary/list.html",
            context={
                LIST_VIEW_CONTEXT_KEY: self.view_model,
            },
            status=None,
        )

    @patch(
        "framework.integrations.django.list_renderer.django_render"
    )
    def test_render_passes_additional_context(
        self,
        django_render_mock,
    ) -> None:
        django_render_mock.return_value = HttpResponse()

        self.renderer.render(
            request=self.request,
            view_model=self.view_model,
            context={
                "page_title": "Sociétés",
            },
        )

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name=DEFAULT_LIST_TEMPLATE_NAME,
            context={
                "page_title": "Sociétés",
                LIST_VIEW_CONTEXT_KEY: self.view_model,
            },
            status=None,
        )

    @patch(
        "framework.integrations.django.list_renderer.django_render"
    )
    def test_render_passes_http_status(
        self,
        django_render_mock,
    ) -> None:
        django_render_mock.return_value = HttpResponse(
            status=202,
        )

        response = self.renderer.render(
            request=self.request,
            view_model=self.view_model,
            status=202,
        )

        self.assertEqual(response.status_code, 202)

        django_render_mock.assert_called_once_with(
            request=self.request,
            template_name=DEFAULT_LIST_TEMPLATE_NAME,
            context={
                LIST_VIEW_CONTEXT_KEY: self.view_model,
            },
            status=202,
        )

    @patch(
        "framework.integrations.django.list_renderer."
        "django_render_to_string"
    )
    def test_render_to_string_returns_html(
        self,
        django_render_to_string_mock,
    ) -> None:
        django_render_to_string_mock.return_value = (
            "<div>content</div>"
        )

        html = self.renderer.render_to_string(
            request=self.request,
            view_model=self.view_model,
        )

        self.assertEqual(
            html,
            "<div>content</div>",
        )

        django_render_to_string_mock.assert_called_once_with(
            template_name=DEFAULT_LIST_TEMPLATE_NAME,
            context={
                LIST_VIEW_CONTEXT_KEY: self.view_model,
            },
            request=self.request,
        )

    def test_real_render_to_string_displays_empty_state(
        self,
    ) -> None:
        html = self.renderer.render_to_string(
            request=self.request,
            view_model=self.view_model,
        )

        self.assertIn(
            "Aucune donnée à afficher.",
            html,
        )

    def test_real_render_returns_http_response(self) -> None:
        response = self.renderer.render(
            request=self.request,
            view_model=self.view_model,
        )

        self.assertIsInstance(
            response,
            HttpResponse,
        )
        self.assertEqual(
            response.status_code,
            200,
        )

    def test_real_render_contains_list_container(self) -> None:
        response = self.renderer.render(
            request=self.request,
            view_model=self.view_model,
        )

        content = response.content.decode("utf-8")

        self.assertIn(
            "edf-list",
            content,
        )


if __name__ == "__main__":
    unittest.main()