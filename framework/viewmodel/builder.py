

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from common.constants import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)
from framework.runtime.eplist import EPList, ListPage
from framework.viewmodel.cell import ViewCell
from framework.viewmodel.column import ViewColumn
from framework.viewmodel.list import ListViewModel
from framework.viewmodel.pagination import PaginationViewModel
from framework.viewmodel.row import ViewRow


class ListViewModelBuilder:
    """Construit un ListViewModel à partir d'une EPList et d'une page."""

    __slots__ = ()

    def build(
        self,
        *,
        runtime: EPList,
        page: ListPage,
        sort_by: str | None = None,
        descending: bool = False,
        visible_column_identifiers: tuple[str, ...] | None = None,
    ) -> ListViewModel:
        """
        Construit un instantané de présentation.

        Lorsque ``visible_column_identifiers`` est absent, les colonnes
        visibles par défaut de la définition sont utilisées.

        Lorsqu'il est fourni, il permet d'appliquer les préférences
        propres à l'utilisateur courant.
        """

        self._validate_runtime(runtime)
        self._validate_page(page)
        self._validate_sort_by(sort_by)
        self._validate_descending(descending)
        self._validate_visible_column_identifiers(
            runtime=runtime,
            visible_column_identifiers=(
                visible_column_identifiers
            ),
        )

        effective_sort = (
            sort_by
            if sort_by is not None
            else runtime.definition.default_sort
        )

        columns = self._build_columns(
            runtime=runtime,
            sort_by=effective_sort,
            descending=descending,
            visible_column_identifiers=(
                visible_column_identifiers
            ),
        )

        rows = self._build_rows(
            runtime=runtime,
            page=page,
            columns=columns,
        )

        pagination = self._build_pagination(page)

        return ListViewModel(
            columns=columns,
            rows=rows,
            pagination=pagination,
        )

    def _build_columns(
        self,
        *,
        runtime: EPList,
        sort_by: str | None,
        descending: bool,
        visible_column_identifiers: tuple[str, ...] | None,
    ) -> tuple[ViewColumn, ...]:
        if visible_column_identifiers is None:
            columns = runtime.visible_columns
        else:
            selected_identifiers = set(
                visible_column_identifiers
            )

            columns = tuple(
                column
                for column in runtime.columns
                if column.identifier in selected_identifiers
            )

        return tuple(
            ViewColumn(
                definition=column,
                sorted=column.identifier == sort_by,
                descending=(
                    descending
                    if column.identifier == sort_by
                    else False
                ),
            )
            for column in columns
        )

    def _build_rows(
        self,
        *,
        runtime: EPList,
        page: ListPage,
        columns: tuple[ViewColumn, ...],
    ) -> tuple[ViewRow, ...]:
        return tuple(
            self._build_row(
                runtime=runtime,
                source_object=source_object,
                columns=columns,
            )
            for source_object in page.rows
        )

    def _build_row(
        self,
        *,
        runtime: EPList,
        source_object,
        columns: tuple[ViewColumn, ...],
    ) -> ViewRow:
        cells = tuple(
            self._build_cell(
                runtime=runtime,
                source_object=source_object,
                column=column,
            )
            for column in columns
        )

        return ViewRow(
            cells=cells,
            source_object=source_object,
            css_class=getattr(
                source_object,
                "row_css_class",
                "",
            ),
        )

    def _build_cell(
        self,
        *,
        runtime: EPList,
        source_object,
        column: ViewColumn,
    ) -> ViewCell:
        value = runtime.get_value(
            source_object,
            column.definition,
        )

        return ViewCell(
            value=value,
            display_value=self._format_display_value(
                value=value,
                data_type=column.definition.field.data_type,
            ),
            column=column,
        )

    def _format_display_value(
        self,
        *,
        value: Any,
        data_type: str,
    ) -> str:
        """Prépare une valeur pour son affichage dans une liste."""

        if value is None:
            return "Aucune"

        if isinstance(value, bool):
            return "Oui" if value else "Non"

        if isinstance(value, datetime):
            return value.strftime(DATETIME_FORMAT)

        if isinstance(value, date):
            return value.strftime(DATE_FORMAT)

        label = getattr(value, "label", None)

        if label is not None:
            return str(label)

        return str(value)

    def _build_pagination(
        self,
        page: ListPage,
    ) -> PaginationViewModel:
        previous_page = (
            page.page - 1
            if page.has_previous
            else None
        )

        next_page = (
            page.page + 1
            if page.has_next
            else None
        )

        return PaginationViewModel(
            page=page.page,
            page_size=page.page_size,
            total_items=page.total_items,
            total_pages=page.total_pages,
            has_previous=page.has_previous,
            has_next=page.has_next,
            previous_page=previous_page,
            next_page=next_page,
        )

    def _validate_runtime(self, runtime: object) -> None:
        if not isinstance(runtime, EPList):
            raise TypeError(
                "La propriété 'runtime' doit être une instance "
                "de EPList."
            )

    def _validate_page(self, page: object) -> None:
        if not isinstance(page, ListPage):
            raise TypeError(
                "La propriété 'page' doit être une instance "
                "de ListPage."
            )

    def _validate_sort_by(self, sort_by: object) -> None:
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

    def _validate_visible_column_identifiers(
        self,
        *,
        runtime: EPList,
        visible_column_identifiers: object,
    ) -> None:
        if visible_column_identifiers is None:
            return

        if not isinstance(
            visible_column_identifiers,
            tuple,
        ):
            raise TypeError(
                "Les identifiants des colonnes visibles doivent "
                "être fournis sous la forme d'un tuple."
            )

        if not visible_column_identifiers:
            raise ValueError(
                "Au moins une colonne doit être visible."
            )

        seen_identifiers = set()

        for identifier in visible_column_identifiers:
            if not isinstance(identifier, str):
                raise TypeError(
                    "Chaque identifiant de colonne visible doit "
                    "être une chaîne de caractères."
                )

            if not identifier.strip():
                raise ValueError(
                    "Un identifiant de colonne visible ne peut "
                    "pas être vide."
                )

            if identifier in seen_identifiers:
                raise ValueError(
                    "Un identifiant de colonne visible ne peut "
                    "pas être présent plusieurs fois."
                )

            if not runtime.definition.has_column(identifier):
                raise ValueError(
                    f"La colonne visible {identifier!r} "
                    "n'existe pas dans cette liste."
                )

            seen_identifiers.add(identifier)