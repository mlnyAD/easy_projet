

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.viewmodel.column import ViewColumn


@dataclass(frozen=True, slots=True)
class ViewCell:
    """Représente une cellule préparée pour une vue."""

    value: Any
    display_value: Any
    column: ViewColumn

    def __post_init__(self) -> None:
        if not isinstance(self.column, ViewColumn):
            raise TypeError(
                "La propriété 'column' doit être une instance "
                "de ViewColumn."
            )

    @property
    def identifier(self) -> str:
        """Retourne l'identifiant de la colonne."""
        return self.column.identifier

    @property
    def label(self) -> str:
        """Retourne le libellé de la colonne."""
        return self.column.label

    @property
    def data_type(self) -> str:
        """Retourne le type métier de la donnée."""
        return self.column.definition.field.data_type

    @property
    def sortable(self) -> bool:
        """Indique si la colonne est triable."""
        return self.column.sortable

    @property
    def visible(self) -> bool:
        """Indique si la colonne est visible."""
        return self.column.visible