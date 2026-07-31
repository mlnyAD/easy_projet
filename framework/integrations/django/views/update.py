

"""
Vue générique de modification Easy Projet.
"""

from django.views.generic import UpdateView

from framework.form import FormMode

from .form import EPFormView


class EPUpdateView(
    EPFormView,
    UpdateView,
):
    """
    Vue générique de modification.
    """

    def get_form_mode(self):
        return FormMode.EDIT