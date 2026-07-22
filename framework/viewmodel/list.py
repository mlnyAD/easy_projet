

from __future__ import annotations

from dataclasses import dataclass

from framework.viewmodel.column import ViewColumn
from framework.viewmodel.pagination import PaginationViewModel
from framework.viewmodel.row import ViewRow


@dataclass(frozen=True, slots=True)
class ListViewModel:
    """Modèle de vue complet d'une liste."""

    columns: tuple[ViewColumn, ...]
    rows: tuple[ViewRow, ...]
    pagination: PaginationViewModel

    def __post_init__(self) -> None:
        if not isinstance(self.columns, tuple):
            raise TypeError(
                "La propriété 'columns' doit être un tuple."
            )

        if not all(
            isinstance(column, ViewColumn)
            for column in self.columns
        ):
            raise TypeError(
                "Chaque élément de 'columns' doit être "
                "une instance de ViewColumn."
            )

        if not isinstance(self.rows, tuple):
            raise TypeError(
                "La propriété 'rows' doit être un tuple."
            )

        if not all(
            isinstance(row, ViewRow)
            for row in self.rows
        ):
            raise TypeError(
                "Chaque élément de 'rows' doit être "
                "une instance de ViewRow."
            )

        if not isinstance(
            self.pagination,
            PaginationViewModel,
        ):
            raise TypeError(
                "La propriété 'pagination' doit être une instance "
                "de PaginationViewModel."
            )

        expected_cell_count = len(self.columns)

        for row in self.rows:
            if len(row.cells) != expected_cell_count:
                raise ValueError(
                    "Chaque ligne doit contenir une cellule "
                    "pour chaque colonne visible."
                )

    def __iter__(self):
        """Permet d'itérer directement sur les lignes."""
        return iter(self.rows)

    def __len__(self) -> int:
        """Retourne le nombre de lignes présentes dans la page."""
        return len(self.rows)