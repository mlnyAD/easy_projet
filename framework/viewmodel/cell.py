

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