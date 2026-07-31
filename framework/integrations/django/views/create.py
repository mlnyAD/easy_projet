

from django.views.generic import CreateView

from framework.form import FormMode

from .form import EPFormView


class EPCreateView(
    EPFormView,
    CreateView,
):
    """
    Vue générique de création.
    """

    def get_form_mode(self):
        return FormMode.CREATE