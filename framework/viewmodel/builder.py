

from __future__ import annotations

from framework.runtime.eplist import EPList, ListPage
from framework.viewmodel.cell import ViewCell
from framework.viewmodel.column import ViewColumn
from framework.viewmodel.list import ListViewModel
from framework.viewmodel.pagination import PaginationViewModel
from framework.viewmodel.row import ViewRow
from datetime import date, datetime
from typing import Any

from common.constants import (
    DATE_FORMAT,
    DATETIME_FORMAT,
)

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
    ) -> ListViewModel:
        """
        Construit un instantané de présentation.

        Lorsque sort_by n'est pas fourni, le tri par défaut de la
        ListDefinition est utilisé pour déterminer l'état des colonnes.
        """
        self._validate_runtime(runtime)
        self._validate_page(page)
        self._validate_sort_by(sort_by)
        self._validate_descending(descending)

        effective_sort = (
            sort_by
            if sort_by is not None
            else runtime.definition.default_sort
        )

        columns = self._build_columns(
            runtime=runtime,
            sort_by=effective_sort,
            descending=descending,
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
    ) -> tuple[ViewColumn, ...]:
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
            for column in runtime.visible_columns
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
        """
        Prépare une valeur pour son affichage dans une liste.
        """

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