

"""
Tests de la vue générique de création Easy Projet.
"""

from django.test import SimpleTestCase

from framework.form import FormMode
from framework.integrations.django.views.create import EPCreateView


class TestEPCreateView(SimpleTestCase):
    """
    Vérifie les contrats de EPCreateView.
    """

    def test_get_form_mode_returns_create(self):
        view = EPCreateView()

        self.assertEqual(view.get_form_mode(), FormMode.CREATE)