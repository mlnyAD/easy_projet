

"""
Construction du contexte Django pour les formulaires Easy Projet.
"""

from collections.abc import Mapping
from typing import Any

from framework.form import EPForm
from framework.viewmodel import FormViewModel

DEFAULT_FORM_TEMPLATE_NAME = "edf/form/view.html"
FORM_VIEW_CONTEXT_KEY = "form_view"

class DjangoFormRenderer:
    """
    Construit le ViewModel destiné aux templates Django.
    """

    def build_view_model(
        self,
        form: EPForm,
        *,
        cancel_url: str | None = None,
    ) -> FormViewModel:
        """
        Construit le ViewModel du formulaire.
        """

        return FormViewModel(
            form=form,
            cancel_url=cancel_url,
        )

class DjangoFormRenderer:
    def build_context(
        self,
        form,
        *,
        cancel_url=None,
        context=None,
    ):
        result = dict(context or {})

        form_view = FormViewModel(
            form=form,
            cancel_url=cancel_url,
        )

        result[FORM_VIEW_CONTEXT_KEY] = form_view

        return result