

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from framework.list.column import ColumnDefinition
from framework.list.definition import ListDefinition
from framework.list.validator import ListValidator
from framework.value_resolver import (
    ValueResolutionError,
    resolve_value,
)

class EPListExecutionError(ValueError):
    """Erreur produite pendant l'exécution d'une EPList."""


@dataclass(frozen=True, slots=True)
class ListPage:
    """
    Résultat paginé produit par EPList.

    Cette structure est indépendante de toute technologie de rendu.
    """

    rows: tuple[Any, ...]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


class EPList:
    """
    Exécute une définition de liste sur un jeu de données.

    EPList prend en charge la validation de la définition, le tri et
    la pagination. Elle ne produit ni HTML ni réponse Django.
    """

    __slots__ = (
        "_definition",
        "_rows",
    )

    def __init__(
        self,
        *,
        definition: ListDefinition,
        rows: Iterable[Any],
    ) -> None:
        self._validate_definition_type(definition)
        self._validate_rows(rows)

        ListValidator().validate(definition)

        self._definition = definition
        self._rows = tuple(rows)

    @property
    def definition(self) -> ListDefinition:
        """Retourne la définition utilisée par la liste."""
        return self._definition

    @property
    def rows(self) -> tuple[Any, ...]:
        """Retourne les données sources dans leur ordre initial."""
        return self._rows

    @property
    def columns(self) -> tuple[ColumnDefinition, ...]:
        """Retourne toutes les colonnes déclarées."""
        return self._definition.columns

    @property
    def visible_columns(self) -> tuple[ColumnDefinition, ...]:
        """Retourne uniquement les colonnes visibles."""
        return self._definition.visible_columns

    @property
    def row_count(self) -> int:
        """Retourne le nombre total de lignes sources."""
        return len(self._rows)

    def get_value(
        self,
        row: Any,
        column: ColumnDefinition,
    ) -> Any:
        """
        Retourne la valeur d'une colonne pour une ligne.

        La résolution de la valeur est déléguée au mécanisme
        transversal du framework.
        """
        field_name = column.field.name

        try:
            return resolve_value(
                row,
                field_name,
            )
        except ValueResolutionError as error:
            if isinstance(row, Mapping):
                message = (
                    f"La ligne ne contient pas le champ "
                    f"{field_name!r}."
                )
            else:
                message = (
                    f"L'objet de type {type(row).__name__!r} "
                    f"ne possède pas l'attribut "
                    f"{field_name!r}."
                )

            raise EPListExecutionError(
                message
            ) from error
                                
    def sort_rows(
        self,
        *,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> tuple[Any, ...]:
        """
        Retourne les lignes triées.

        Lorsque sort_by vaut None, la colonne default_sort de la définition
        est utilisée. Si aucun tri n'est défini, l'ordre source est conservé.
        """
        self._validate_sort_by(sort_by)
        self._validate_descending(descending)

        effective_sort = (
            sort_by
            if sort_by is not None
            else self._definition.default_sort
        )

        if effective_sort is None:
            return self._rows

        column = self._get_sort_column(effective_sort)

        rows_with_value: list[tuple[Any, Any]] = []
        rows_without_value: list[Any] = []

        for row in self._rows:
            value = self.get_value(row, column)

            if value is None:
                rows_without_value.append(row)
            else:
                rows_with_value.append((value, row))

        try:
            rows_with_value.sort(
                key=lambda item: item[0],
                reverse=descending,
            )
        except TypeError as exc:
            raise EPListExecutionError(
                "Les valeurs de la colonne "
                f"{effective_sort!r} ne peuvent pas être triées ensemble."
            ) from exc

        sorted_rows = [
            row
            for _, row in rows_with_value
        ]
        sorted_rows.extend(rows_without_value)

        return tuple(sorted_rows)

    def paginate(
        self,
        *,
        page: int = 1,
        page_size: int | None = None,
        sort_by: str | None = None,
        descending: bool = False,
    ) -> ListPage:
        """
        Trie puis pagine les données.

        Si page_size n'est pas fourni, la valeur définie dans
        ListDefinition est utilisée.
        """
        self._validate_page(page)
        self._validate_optional_page_size(page_size)

        effective_page_size = (
            page_size
            if page_size is not None
            else self._definition.page_size
        )

        sorted_rows = self.sort_rows(
            sort_by=sort_by,
            descending=descending,
        )

        total_items = len(sorted_rows)
        total_pages = (
            (total_items + effective_page_size - 1)
            // effective_page_size
        )

        start = (page - 1) * effective_page_size
        end = start + effective_page_size
        page_rows = sorted_rows[start:end]

        return ListPage(
            rows=page_rows,
            page=page,
            page_size=effective_page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_previous=page > 1 and total_pages > 0,
            has_next=page < total_pages,
        )

    def _get_sort_column(
        self,
        identifier: str,
    ) -> ColumnDefinition:
        if not self._definition.has_column(identifier):
            raise EPListExecutionError(
                f"La colonne de tri {identifier!r} n'existe pas."
            )

        column = self._definition.get_column(identifier)

        if not column.sortable:
            raise EPListExecutionError(
                f"La colonne {identifier!r} n'est pas triable."
            )

        return column

    def _validate_definition_type(
        self,
        definition: object,
    ) -> None:
        if not isinstance(definition, ListDefinition):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de ListDefinition."
            )

    def _validate_rows(self, rows: object) -> None:
        if isinstance(rows, (str, bytes)):
            raise TypeError(
                "La propriété 'rows' doit être un itérable de lignes."
            )

        if not isinstance(rows, Iterable):
            raise TypeError(
                "La propriété 'rows' doit être un itérable de lignes."
            )

    def _validate_sort_by(
        self,
        sort_by: object,
    ) -> None:
        if sort_by is None:
            return

        if not isinstance(sort_by, str):
            raise TypeError(
                "La propriété 'sort_by' doit être une chaîne "
                "de caractères."
            )

        if not sort_by.strip():
            raise ValueError(
                "La propriété 'sort_by' ne peut pas être vide."
            )

    def _validate_descending(
        self,
        descending: object,
    ) -> None:
        if not isinstance(descending, bool):
            raise TypeError(
                "La propriété 'descending' doit être un booléen."
            )

    def _validate_page(self, page: object) -> None:
        if isinstance(page, bool) or not isinstance(page, int):
            raise TypeError(
                "La propriété 'page' doit être un entier."
            )

        if page <= 0:
            raise ValueError(
                "La propriété 'page' doit être strictement positive."
            )

    def _validate_optional_page_size(
        self,
        page_size: object,
    ) -> None:
        if page_size is None:
            return

        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError(
                "La propriété 'page_size' doit être un entier."
            )

        if page_size <= 0:
            raise ValueError(
                "La propriété 'page_size' doit être strictement positive."
            )

    def __iter__(self):
        """Permet d'itérer directement sur les lignes sources."""
        return iter(self._rows)

    def __len__(self) -> int:
        """Retourne le nombre de lignes sources."""
        return len(self._rows)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"entity={self.definition.entity.name!r}, "
            f"rows={self.row_count}, "
            f"columns={len(self.columns)}"
            f")"
        )