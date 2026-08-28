

"""
Cellule d'une collection de formulaire prête à être affichée.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.forms.boundfield import BoundField

from framework.form.collection import (
    FormCollectionColumnDefinition,
)


@dataclass(frozen=True, slots=True)
class ResolvedFormCollectionCell:
    """
    Représente une cellule résolue d'une collection.

    Une cellule contient soit un champ Django éditable,
    soit une valeur destinée uniquement à l'affichage.
    """

    definition: FormCollectionColumnDefinition

    bound_field: BoundField | None = None

    display_value: object | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.definition,
            FormCollectionColumnDefinition,
        ):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de FormCollectionColumnDefinition."
            )

        if (
            self.bound_field is not None
            and not isinstance(
                self.bound_field,
                BoundField,
            )
        ):
            raise TypeError(
                "La propriété 'bound_field' doit être une instance "
                "de BoundField ou None."
            )

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def label(self) -> str:
        return (
            self.definition.label
            or self.definition.name
        )

    @property
    def editable(self) -> bool:
        return (
            self.bound_field is not None
            and not self.definition.readonly
        )

    @property
    def errors(self):
        if self.bound_field is None:
            return ()

        return self.bound_field.errors