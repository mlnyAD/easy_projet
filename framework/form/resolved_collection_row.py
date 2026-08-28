

"""
Ligne d'une collection de formulaire prête à être affichée.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.forms.forms import BaseForm

from framework.form.resolved_collection_cell import (
    ResolvedFormCollectionCell,
)


@dataclass(frozen=True, slots=True)
class ResolvedFormCollectionRow:
    """
    Représente une ligne résolue d'une collection.
    """

    django_form: BaseForm

    cells: list[ResolvedFormCollectionCell] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        if not isinstance(
            self.django_form,
            BaseForm,
        ):
            raise TypeError(
                "La propriété 'django_form' doit être une instance "
                "de BaseForm."
            )

    @property
    def delete_field(self):
        """
        Retourne le champ DELETE du formset lorsqu'il existe.
        """
        try:
            return self.django_form["DELETE"]
        except KeyError:
            return None