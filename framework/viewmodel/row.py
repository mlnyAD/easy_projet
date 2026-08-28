

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from framework.viewmodel.cell import ViewCell


@dataclass(frozen=True, slots=True)
class ViewRow:
    """Représente une ligne préparée pour une vue."""

    cells: tuple[ViewCell, ...]
    source_object: Any
    css_class: str = ""

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

        if not isinstance(
            self.css_class,
            str,
        ):
            raise TypeError(
                "La propriété 'css_class' doit être "
                "une chaîne de caractères."
            )

    def __iter__(self):
        return iter(self.cells)

    def __len__(self) -> int:
        return len(self.cells)