

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.viewmodel.cell import ViewCell


@dataclass(frozen=True, slots=True)
class ViewRow:
    """Représente une ligne préparée pour une vue."""

    cells: tuple[ViewCell, ...]
    source_object: Any

    def __post_init__(self) -> None:
        if not isinstance(self.cells, tuple):
            raise TypeError(
                "La propriété 'cells' doit être un tuple."
            )

        if not all(
            isinstance(cell, ViewCell)
            for cell in self.cells
        ):
            raise TypeError(
                "Chaque élément de 'cells' doit être "
                "une instance de ViewCell."
            )

    def __iter__(self):
        """Permet d'itérer directement sur les cellules."""
        return iter(self.cells)

    def __len__(self) -> int:
        """Retourne le nombre de cellules."""
        return len(self.cells)