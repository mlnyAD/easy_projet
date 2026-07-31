

"""
Tests de la vue générique de modification Easy Projet.
"""

from django.test import SimpleTestCase

from framework.form import FormMode
from framework.integrations.django.views.update import EPUpdateView


class TestEPUpdateView(SimpleTestCase):
    """
    Vérifie les contrats de EPUpdateView.
    """

    def test_get_form_mode_returns_edit(self):
        view = EPUpdateView()

        self.assertEqual(view.get_form_mode(), FormMode.EDIT)