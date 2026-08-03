

"""
Construction du contexte Django pour les formulaires Easy Projet.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from framework.form import EPForm
from framework.viewmodel import FormViewModel


DEFAULT_FORM_TEMPLATE_NAME = "edf/form/view.html"
FORM_VIEW_CONTEXT_KEY = "form_view"


class DjangoFormRenderer:
    """
    Construit le ViewModel et le contexte destinés aux templates Django.

    Le rendu HTTP reste assuré par les vues génériques Django.
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
        self._validate_form(form)

        return FormViewModel(
            form=form,
            cancel_url=cancel_url,
        )

    def build_context(
        self,
        form: EPForm,
        *,
        cancel_url: str | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Ajoute le FormViewModel au contexte Django existant.
        """
        self._validate_form(form)

        if context is None:
            result: dict[str, Any] = {}
        else:
            if not isinstance(context, Mapping):
                raise TypeError(
                    "La propriété 'context' doit être un Mapping."
                )

            if FORM_VIEW_CONTEXT_KEY in context:
                raise ValueError(
                    f"La clé {FORM_VIEW_CONTEXT_KEY!r} est réservée "
                    "au renderer."
                )

            result = dict(context)

        result[FORM_VIEW_CONTEXT_KEY] = (
            self.build_view_model(
                form,
                cancel_url=cancel_url,
            )
        )

        return result

    @staticmethod
    def _validate_form(form: object) -> None:
        if not isinstance(form, EPForm):
            raise TypeError(
                "La propriété 'form' doit être une instance de EPForm."
            )