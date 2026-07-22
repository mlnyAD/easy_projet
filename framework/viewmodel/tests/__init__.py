

import unittest
from dataclasses import FrozenInstanceError, dataclass

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition
from framework.list.definition import ListDefinition
from framework.runtime.eplist import EPList
from framework.viewmodel import (
    ListViewModel,
    ListViewModelBuilder,
    PaginationViewModel,
    ViewCell,
    ViewColumn,
    ViewRow,
)


@dataclass
class CompanyRow:
    code: str
    name: str
    city: str | None


class ListViewModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.entity = EntityDefinition(
            {
                "entity": {
                    "name": "company",
                    "label": "Société",
                    "label_plural": "Sociétés",
                    "description": "Société cliente ou intervenante.",
                },
                "fields": {
                    "code": {
                        "label": "Code",
                        "data_type": "string",
                        "required": True,
                        "unique": True,
                        "max_length": 10,
                    },
                    "name": {
                        "label": "Nom",
                        "data_type": "string",
                        "required": True,
                        "max_length": 150,
                    },
                    "city": {
                        "label": "Ville",
                        "data_type": "string",
                        "required": False,
                        "max_length": 100,
                    },
                },
            }
        )

        self.code_column = ColumnDefinition(
            field=self.entity.get_field("code"),
            order=1,
        )
        self.name_column = ColumnDefinition(
            field=self.entity.get_field("name"),
            order=2,
        )
        self.city_column = ColumnDefinition(
            field=self.entity.get_field("city"),
            visible=False,
            order=3,
        )

        self.definition = ListDefinition(
            entity=self.entity,
            columns=[
                self.code_column,
                self.name_column,
                self.city_column,
            ],
            default_sort="name",
            page_size=2,
        )

        self.rows = [
            {
                "code": "C003",
                "name": "Gamma",
                "city": None,
            },
            {
                "code": "C001",
                "name": "Alpha",
                "city": "Paris",
            },
            {
                "code": "C002",
                "name": "Beta",
                "city": "Lyon",
            },
        ]

        self.runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.builder = ListViewModelBuilder()

    def test_view_column_delegates_definition_properties(self) -> None:
        column = ViewColumn(
            definition=self.code_column,
        )

        self.assertEqual(column.identifier, "code")
        self.assertEqual(column.label, self.code_column.label)
        self.assertTrue(column.visible)
        self.assertTrue(column.sortable)
        self.assertEqual(column.order, 1)

    def test_descending_column_must_be_sorted(self) -> None:
        with self.assertRaises(ValueError):
            ViewColumn(
                definition=self.code_column,
                sorted=False,
                descending=True,
            )

    def test_view_cell_creation(self) -> None:
        column = ViewColumn(
            definition=self.code_column,
        )

        cell = ViewCell(
            value="C001",
            display_value="C001",
            column=column,
        )

        self.assertEqual(cell.value, "C001")
        self.assertEqual(cell.display_value, "C001")
        self.assertIs(cell.column, column)

    def test_view_row_creation(self) -> None:
        column = ViewColumn(
            definition=self.code_column,
        )
        cell = ViewCell(
            value="C001",
            display_value="C001",
            column=column,
        )
        source = {"code": "C001"}

        row = ViewRow(
            cells=(cell,),
            source_object=source,
        )

        self.assertEqual(row.cells, (cell,))
        self.assertIs(row.source_object, source)
        self.assertEqual(len(row), 1)
        self.assertEqual(list(row), [cell])

    def test_pagination_creation(self) -> None:
        pagination = PaginationViewModel(
            page=2,
            page_size=20,
            total_items=45,
            total_pages=3,
            has_previous=True,
            has_next=True,
            previous_page=1,
            next_page=3,
        )

        self.assertEqual(pagination.previous_page, 1)
        self.assertEqual(pagination.next_page, 3)

    def test_inconsistent_previous_page_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PaginationViewModel(
                page=2,
                page_size=20,
                total_items=45,
                total_pages=3,
                has_previous=True,
                has_next=True,
                previous_page=None,
                next_page=3,
            )

    def test_builder_returns_list_view_model(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        self.assertIsInstance(view, ListViewModel)

    def test_builder_uses_visible_columns_only(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        self.assertEqual(
            [
                column.identifier
                for column in view.columns
            ],
            ["code", "name"],
        )

    def test_builder_preserves_visible_column_order(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        self.assertIs(
            view.columns[0].definition,
            self.code_column,
        )
        self.assertIs(
            view.columns[1].definition,
            self.name_column,
        )

    def test_builder_marks_default_sort_column(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        code_column, name_column = view.columns

        self.assertFalse(code_column.sorted)
        self.assertTrue(name_column.sorted)
        self.assertFalse(name_column.descending)

    def test_builder_marks_explicit_sort_column(self) -> None:
        page = self.runtime.paginate(
            page=1,
            sort_by="code",
            descending=True,
        )

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
            sort_by="code",
            descending=True,
        )

        code_column, name_column = view.columns

        self.assertTrue(code_column.sorted)
        self.assertTrue(code_column.descending)
        self.assertFalse(name_column.sorted)
        self.assertFalse(name_column.descending)

    def test_builder_builds_rows_in_page_order(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        self.assertEqual(
            [
                row.source_object["name"]
                for row in view.rows
            ],
            ["Alpha", "Beta"],
        )

    def test_builder_builds_one_cell_per_visible_column(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        self.assertEqual(len(view.rows), 2)
        self.assertEqual(len(view.rows[0].cells), 2)
        self.assertEqual(len(view.rows[1].cells), 2)

    def test_builder_preserves_raw_values(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        first_row = view.rows[0]

        self.assertEqual(first_row.cells[0].value, "C001")
        self.assertEqual(first_row.cells[1].value, "Alpha")

    def test_display_value_equals_raw_value(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        for row in view.rows:
            for cell in row.cells:
                self.assertEqual(
                    cell.display_value,
                    cell.value,
                )

    def test_hidden_column_does_not_generate_cells(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        identifiers = [
            cell.column.identifier
            for cell in view.rows[0].cells
        ]

        self.assertNotIn("city", identifiers)

    def test_builder_supports_object_rows(self) -> None:
        rows = [
            CompanyRow(
                code="C002",
                name="Beta",
                city=None,
            ),
            CompanyRow(
                code="C001",
                name="Alpha",
                city="Paris",
            ),
        ]

        runtime = EPList(
            definition=self.definition,
            rows=rows,
        )
        page = runtime.paginate()

        view = self.builder.build(
            runtime=runtime,
            page=page,
        )

        self.assertEqual(
            view.rows[0].cells[0].value,
            "C001",
        )
        self.assertEqual(
            view.rows[0].cells[1].value,
            "Alpha",
        )
        self.assertIs(
            view.rows[0].source_object,
            rows[1],
        )

    def test_none_value_is_preserved(self) -> None:
        visible_city_column = ColumnDefinition(
            field=self.entity.get_field("city"),
            visible=True,
            order=3,
        )

        definition = ListDefinition(
            entity=self.entity,
            columns=[
                self.code_column,
                self.name_column,
                visible_city_column,
            ],
            default_sort="name",
            page_size=10,
        )

        runtime = EPList(
            definition=definition,
            rows=self.rows,
        )
        page = runtime.paginate()

        view = self.builder.build(
            runtime=runtime,
            page=page,
        )

        gamma_row = next(
            row
            for row in view.rows
            if row.source_object["name"] == "Gamma"
        )

        self.assertIsNone(gamma_row.cells[2].value)
        self.assertIsNone(gamma_row.cells[2].display_value)

    def test_builder_builds_pagination(self) -> None:
        page = self.runtime.paginate(page=1)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        pagination = view.pagination

        self.assertEqual(pagination.page, 1)
        self.assertEqual(pagination.page_size, 2)
        self.assertEqual(pagination.total_items, 3)
        self.assertEqual(pagination.total_pages, 2)
        self.assertFalse(pagination.has_previous)
        self.assertTrue(pagination.has_next)
        self.assertIsNone(pagination.previous_page)
        self.assertEqual(pagination.next_page, 2)

    def test_second_page_pagination(self) -> None:
        page = self.runtime.paginate(page=2)

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        pagination = view.pagination

        self.assertTrue(pagination.has_previous)
        self.assertFalse(pagination.has_next)
        self.assertEqual(pagination.previous_page, 1)
        self.assertIsNone(pagination.next_page)

    def test_empty_dataset(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=[],
        )
        page = runtime.paginate()

        view = self.builder.build(
            runtime=runtime,
            page=page,
        )

        self.assertEqual(view.rows, ())
        self.assertEqual(view.pagination.total_items, 0)
        self.assertEqual(view.pagination.total_pages, 0)

    def test_list_view_model_is_immutable(self) -> None:
        page = self.runtime.paginate()

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        with self.assertRaises(FrozenInstanceError):
            view.rows = ()

    def test_nested_objects_are_immutable(self) -> None:
        page = self.runtime.paginate()

        view = self.builder.build(
            runtime=self.runtime,
            page=page,
        )

        with self.assertRaises(FrozenInstanceError):
            view.columns[0].sorted = True

        with self.assertRaises(FrozenInstanceError):
            view.rows[0].cells[0].value = "CHANGED"

        with self.assertRaises(FrozenInstanceError):
            view.pagination.page = 2

    def test_runtime_type_is_validated(self) -> None:
        page = self.runtime.paginate()

        with self.assertRaises(TypeError):
            self.builder.build(
                runtime="runtime",
                page=page,
            )

    def test_page_type_is_validated(self) -> None:
        with self.assertRaises(TypeError):
            self.builder.build(
                runtime=self.runtime,
                page="page",
            )

    def test_sort_by_type_is_validated(self) -> None:
        page = self.runtime.paginate()

        with self.assertRaises(TypeError):
            self.builder.build(
                runtime=self.runtime,
                page=page,
                sort_by=123,
            )

    def test_blank_sort_by_is_rejected(self) -> None:
        page = self.runtime.paginate()

        with self.assertRaises(ValueError):
            self.builder.build(
                runtime=self.runtime,
                page=page,
                sort_by="   ",
            )

    def test_descending_type_is_validated(self) -> None:
        page = self.runtime.paginate()

        with self.assertRaises(TypeError):
            self.builder.build(
                runtime=self.runtime,
                page=page,
                descending=1,
            )

    def test_row_cell_count_must_match_columns(self) -> None:
        column = ViewColumn(
            definition=self.code_column,
        )
        row = ViewRow(
            cells=(),
            source_object=self.rows[0],
        )
        pagination = PaginationViewModel(
            page=1,
            page_size=20,
            total_items=1,
            total_pages=1,
            has_previous=False,
            has_next=False,
            previous_page=None,
            next_page=None,
        )

        with self.assertRaises(ValueError):
            ListViewModel(
                columns=(column,),
                rows=(row,),
                pagination=pagination,
            )


if __name__ == "__main__":
    unittest.main()