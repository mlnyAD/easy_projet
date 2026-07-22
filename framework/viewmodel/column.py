

from __future__ import annotations

from dataclasses import dataclass

from framework.list.column import ColumnDefinition


@dataclass(frozen=True, slots=True)
class ViewColumn:
    """Représente l'état d'affichage d'une colonne."""

    definition: ColumnDefinition
    sorted: bool = False
    descending: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.definition, ColumnDefinition):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de ColumnDefinition."
            )

        if not isinstance(self.sorted, bool):
            raise TypeError(
                "La propriété 'sorted' doit être un booléen."
            )

        if not isinstance(self.descending, bool):
            raise TypeError(
                "La propriété 'descending' doit être un booléen."
            )

        if self.descending and not self.sorted:
            raise ValueError(
                "Une colonne ne peut pas être descendante "
                "si elle n'est pas triée."
            )

    @property
    def identifier(self) -> str:
        """Retourne l'identifiant de la colonne."""
        return self.definition.identifier

    @property
    def label(self) -> str:
        """Retourne le libellé de la colonne."""
        return self.definition.label

    @property
    def visible(self) -> bool:
        """Indique si la colonne est visible."""
        return self.definition.visible

    @property
    def sortable(self) -> bool:
        """Indique si la colonne est triable."""
        return self.definition.sortable

    @property
    def width(self):
        """Retourne la largeur déclarée de la colonne."""
        return self.definition.width

    @property
    def order(self) -> int:
        """Retourne l'ordre déclaré de la colonne."""
        return self.definition.order