

"""
ViewModel utilisé pour le rendu d'un formulaire Easy Projet.
"""

from dataclasses import dataclass
from typing import Any

from framework.form import (
    EPForm,
    FormMode,
    ResolvedFormCollection,
    ResolvedSection,
)


@dataclass(frozen=True, slots=True)
class FormViewModel:
    """
    Données nécessaires au rendu d'un formulaire.

    Le ViewModel constitue l'unique interface entre le renderer
    Django et les templates génériques.
    """

    form: EPForm
    cancel_url: str | None

    @property
    def is_readonly(self) -> bool:
        """
        Indique si le formulaire est affiché en lecture seule.
        """
        return self.form.is_readonly

    @property
    def django_form(self) -> Any:
        """
        Retourne le ModelForm Django porté par EPForm.
        """
        return self.form.django_form

    @property
    def title(self) -> str:
        return self.form.title

    @property
    def sections(self) -> list[ResolvedSection]:
        return self.form.sections

    @property
    def collections(self) -> list[ResolvedFormCollection]:
        """
        Retourne les collections répétables du formulaire.
        """
        return self.form.collections

    @property
    def mode(self) -> FormMode:
        return self.form.mode