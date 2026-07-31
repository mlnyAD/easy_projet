

"""
Tests du mixin commun aux vues Easy Projet.
"""

from django.test import SimpleTestCase

from framework.context.context import EPContext
from framework.integrations.django.views.base import EPViewMixin
from framework.providers import ProviderRegistry


class TestEPViewMixin(SimpleTestCase):
    """
    Vérifie les contrats exposés par EPViewMixin.
    """

    def test_get_ep_context_returns_ep_context(self):
        view = EPViewMixin()

        context = view.get_ep_context()

        self.assertIsInstance(context, EPContext)

    def test_get_ep_context_initializes_empty_context(self):
        view = EPViewMixin()

        context = view.get_ep_context()

        self.assertIsNone(context.operator)
        self.assertIsNone(context.client_environment)
        self.assertIsNone(context.company)
        self.assertIsNone(context.project)

    def test_get_provider_registry_returns_provider_registry(self):
        view = EPViewMixin()

        registry = view.get_provider_registry()

        self.assertIsInstance(registry, ProviderRegistry)

    def test_get_provider_registry_returns_new_registry(self):
        view = EPViewMixin()

        first_registry = view.get_provider_registry()
        second_registry = view.get_provider_registry()

        self.assertIsNot(first_registry, second_registry)

    def test_get_cancel_url_returns_none_when_no_url_is_defined(self):
        view = EPViewMixin()

        cancel_url = view.get_cancel_url()

        self.assertIsNone(cancel_url)

    def test_get_cancel_url_returns_success_url_as_string(self):
        view = EPViewMixin()
        view.success_url = "/companies/"

        cancel_url = view.get_cancel_url()

        self.assertEqual(cancel_url, "/companies/")
        self.assertIsInstance(cancel_url, str)

    def test_get_cancel_url_prioritizes_cancel_url(self):
        view = EPViewMixin()
        view.cancel_url = "/companies/cancel/"
        view.success_url = "/companies/"

        cancel_url = view.get_cancel_url()

        self.assertEqual(cancel_url, "/companies/cancel/")

    def test_get_cancel_url_returns_cancel_url_as_string(self):
        view = EPViewMixin()
        view.cancel_url = 123

        cancel_url = view.get_cancel_url()

        self.assertEqual(cancel_url, "123")
        self.assertIsInstance(cancel_url, str)