

from __future__ import annotations

from collections.abc import Iterator, Sequence
from types import MappingProxyType
from typing import Final

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition


DEFAULT_PAGE_SIZE: Final[int] = 20


class ListDefinition:
    """
    Décrit une liste du Framework Easy Projet.

    Cette classe contient uniquement la définition structurelle d'une liste.
    Elle ne dépend ni de Django, ni d'une base de données, ni d'une technologie
    de rendu.
    """

    __slots__ = (
        "_entity",
        "_columns",
        "_columns_by_identifier",
        "_default_sort",
        "_page_size",
    )

    def __init__(
        self,
        *,
        entity: EntityDefinition,
        columns: Sequence[ColumnDefinition],
        default_sort: str | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        self._validate_entity(entity)
        self._validate_columns(columns)
        self._validate_default_sort(default_sort)
        self._validate_page_size(page_size)

        normalized_columns = tuple(columns)

        self._entity = entity
        self._columns = normalized_columns
        self._columns_by_identifier = MappingProxyType(
            {
                column.identifier: column
                for column in normalized_columns
            }
        )
        self._default_sort = default_sort
        self._page_size = page_size

    @property
    def entity(self) -> EntityDefinition:
        """Retourne l'entité décrite par la liste."""
        return self._entity

    @property
    def columns(self) -> tuple[ColumnDefinition, ...]:
        """Retourne les colonnes dans leur ordre de déclaration."""
        return self._columns

    @property
    def columns_by_identifier(
        self,
    ) -> MappingProxyType[str, ColumnDefinition]:
        """Retourne l'index immuable des colonnes par identifiant."""
        return self._columns_by_identifier

    @property
    def default_sort(self) -> str | None:
        """Retourne l'identifiant de la colonne de tri par défaut."""
        return self._default_sort

    @property
    def page_size(self) -> int:
        """Retourne le nombre d'éléments par page."""
        return self._page_size

    @property
    def column_identifiers(self) -> tuple[str, ...]:
        """Retourne les identifiants des colonnes."""
        return tuple(
            column.identifier
            for column in self._columns
        )

    @property
    def visible_columns(self) -> tuple[ColumnDefinition, ...]:
        """Retourne uniquement les colonnes visibles."""
        return tuple(
            column
            for column in self._columns
            if column.visible
        )

    def has_column(self, identifier: str) -> bool:
        """Indique si une colonne existe."""
        return identifier in self._columns_by_identifier

    def get_column(self, identifier: str) -> ColumnDefinition:
        """
        Retourne une colonne par son identifiant.

        Lève KeyError lorsque la colonne n'existe pas.
        """
        return self._columns_by_identifier[identifier]

    def __iter__(self) -> Iterator[ColumnDefinition]:
        """Permet d'itérer directement sur les colonnes."""
        return iter(self._columns)

    def __len__(self) -> int:
        """Retourne le nombre de colonnes."""
        return len(self._columns)

    def __contains__(self, identifier: object) -> bool:
        """Permet d'utiliser l'opérateur `in` avec un identifiant."""
        return identifier in self._columns_by_identifier

    def _validate_entity(self, entity: object) -> None:
        if not isinstance(entity, EntityDefinition):
            raise TypeError(
                "La propriété 'entity' doit être une instance "
                "de EntityDefinition."
            )

    def _validate_columns(
        self,
        columns: object,
    ) -> None:
        if isinstance(columns, (str, bytes)):
            raise TypeError(
                "La propriété 'columns' doit être une séquence "
                "de ColumnDefinition."
            )

        if not isinstance(columns, Sequence):
            raise TypeError(
                "La propriété 'columns' doit être une séquence "
                "de ColumnDefinition."
            )

        if not columns:
            raise ValueError(
                "La propriété 'columns' doit contenir au moins une colonne."
            )

        for index, column in enumerate(columns):
            if not isinstance(column, ColumnDefinition):
                raise TypeError(
                    "La colonne située à l'index "
                    f"{index} doit être une instance de ColumnDefinition."
                )

    def _validate_default_sort(
        self,
        default_sort: object,
    ) -> None:
        if default_sort is None:
            return

        if not isinstance(default_sort, str):
            raise TypeError(
                "La propriété 'default_sort' doit être une chaîne "
                "de caractères."
            )

        if not default_sort.strip():
            raise ValueError(
                "La propriété 'default_sort' ne peut pas être vide."
            )

    def _validate_page_size(
        self,
        page_size: object,
    ) -> None:
        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError(
                "La propriété 'page_size' doit être un entier."
            )

        if page_size <= 0:
            raise ValueError(
                "La propriété 'page_size' doit être strictement positive."
            )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"entity={self.entity.name!r}, "
            f"columns={len(self.columns)}, "
            f"default_sort={self.default_sort!r}, "
            f"page_size={self.page_size}"
            f")"
        )