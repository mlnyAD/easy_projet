

import unittest
from dataclasses import FrozenInstanceError, dataclass

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition
from framework.list.definition import ListDefinition
from framework.runtime.eplist import (
    EPList,
    EPListExecutionError,
    ListPage,
)


@dataclass
class CompanyRow:
    code: str
    name: str
    city: str | None


class EPListTests(unittest.TestCase):
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
        )
        self.name_column = ColumnDefinition(
            field=self.entity.get_field("name"),
        )
        self.city_column = ColumnDefinition(
            field=self.entity.get_field("city"),
            visible=False,
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

    def test_creation(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertIs(runtime.definition, self.definition)
        self.assertEqual(runtime.rows, tuple(self.rows))

    def test_rows_are_copied_to_tuple(self) -> None:
        source_rows = list(self.rows)

        runtime = EPList(
            definition=self.definition,
            rows=source_rows,
        )

        source_rows.append(
            {
                "code": "C004",
                "name": "Delta",
                "city": "Nice",
            }
        )

        self.assertEqual(len(runtime.rows), 3)

    def test_columns(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(
            runtime.columns,
            self.definition.columns,
        )

    def test_visible_columns(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(
            runtime.visible_columns,
            (
                self.code_column,
                self.name_column,
            ),
        )

    def test_row_count(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(runtime.row_count, 3)

    def test_len(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(len(runtime), 3)

    def test_iteration(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(
            list(runtime),
            self.rows,
        )

    def test_get_value_from_mapping(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        value = runtime.get_value(
            self.rows[0],
            self.name_column,
        )

        self.assertEqual(value, "Gamma")

    def test_get_value_from_object(self) -> None:
        row = CompanyRow(
            code="C001",
            name="Alpha",
            city="Paris",
        )

        runtime = EPList(
            definition=self.definition,
            rows=[row],
        )

        value = runtime.get_value(
            row,
            self.name_column,
        )

        self.assertEqual(value, "Alpha")

    def test_missing_mapping_field_is_rejected(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=[{"code": "C001"}],
        )

        with self.assertRaisesRegex(
            EPListExecutionError,
            "ne contient pas le champ 'name'",
        ):
            runtime.get_value(
                runtime.rows[0],
                self.name_column,
            )

    def test_missing_object_attribute_is_rejected(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=[object()],
        )

        with self.assertRaisesRegex(
            EPListExecutionError,
            "ne possède pas l'attribut 'name'",
        ):
            runtime.get_value(
                runtime.rows[0],
                self.name_column,
            )

    def test_default_sort_is_applied(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        sorted_rows = runtime.sort_rows()

        self.assertEqual(
            [row["name"] for row in sorted_rows],
            ["Alpha", "Beta", "Gamma"],
        )

    def test_explicit_sort_overrides_default_sort(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        sorted_rows = runtime.sort_rows(sort_by="code")

        self.assertEqual(
            [row["code"] for row in sorted_rows],
            ["C001", "C002", "C003"],
        )

    def test_descending_sort(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        sorted_rows = runtime.sort_rows(
            sort_by="name",
            descending=True,
        )

        self.assertEqual(
            [row["name"] for row in sorted_rows],
            ["Gamma", "Beta", "Alpha"],
        )

    def test_none_values_are_placed_last(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        sorted_rows = runtime.sort_rows(sort_by="city")

        self.assertEqual(
            [row["city"] for row in sorted_rows],
            ["Lyon", "Paris", None],
        )

    def test_source_order_is_preserved_without_sort(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=[
                self.code_column,
                self.name_column,
            ],
        )

        runtime = EPList(
            definition=definition,
            rows=self.rows,
        )

        self.assertEqual(
            runtime.sort_rows(),
            tuple(self.rows),
        )

    def test_unknown_sort_column_is_rejected(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaisesRegex(
            EPListExecutionError,
            "colonne de tri 'unknown' n'existe pas",
        ):
            runtime.sort_rows(sort_by="unknown")

    def test_non_sortable_column_is_rejected(self) -> None:
        city_column = ColumnDefinition(
            field=self.entity.get_field("city"),
            sortable=False,
        )

        definition = ListDefinition(
            entity=self.entity,
            columns=[
                self.code_column,
                self.name_column,
                city_column,
            ],
        )

        runtime = EPList(
            definition=definition,
            rows=self.rows,
        )

        with self.assertRaisesRegex(
            EPListExecutionError,
            "'city' n'est pas triable",
        ):
            runtime.sort_rows(sort_by="city")

    def test_first_page(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        result = runtime.paginate(page=1)

        self.assertIsInstance(result, ListPage)
        self.assertEqual(
            [row["name"] for row in result.rows],
            ["Alpha", "Beta"],
        )
        self.assertEqual(result.page, 1)
        self.assertEqual(result.page_size, 2)
        self.assertEqual(result.total_items, 3)
        self.assertEqual(result.total_pages, 2)
        self.assertFalse(result.has_previous)
        self.assertTrue(result.has_next)

    def test_second_page(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        result = runtime.paginate(page=2)

        self.assertEqual(
            [row["name"] for row in result.rows],
            ["Gamma"],
        )
        self.assertTrue(result.has_previous)
        self.assertFalse(result.has_next)

    def test_custom_page_size(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        result = runtime.paginate(
            page=1,
            page_size=1,
        )

        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.page_size, 1)
        self.assertEqual(result.total_pages, 3)

    def test_page_beyond_last_page_is_empty(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        result = runtime.paginate(page=4)

        self.assertEqual(result.rows, ())
        self.assertEqual(result.page, 4)
        self.assertFalse(result.has_next)

    def test_empty_dataset(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=[],
        )

        result = runtime.paginate()

        self.assertEqual(result.rows, ())
        self.assertEqual(result.total_items, 0)
        self.assertEqual(result.total_pages, 0)
        self.assertFalse(result.has_previous)
        self.assertFalse(result.has_next)

    def test_list_page_is_immutable(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        result = runtime.paginate()

        with self.assertRaises(FrozenInstanceError):
            result.page = 2

    def test_invalid_definition_type(self) -> None:
        with self.assertRaises(TypeError):
            EPList(
                definition="company",
                rows=self.rows,
            )

    def test_rows_must_be_iterable(self) -> None:
        with self.assertRaises(TypeError):
            EPList(
                definition=self.definition,
                rows=123,
            )

    def test_rows_cannot_be_a_string(self) -> None:
        with self.assertRaises(TypeError):
            EPList(
                definition=self.definition,
                rows="companies",
            )

    def test_sort_by_must_be_a_string(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(TypeError):
            runtime.sort_rows(sort_by=123)

    def test_sort_by_cannot_be_blank(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(ValueError):
            runtime.sort_rows(sort_by="   ")

    def test_descending_must_be_boolean(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(TypeError):
            runtime.sort_rows(descending=1)

    def test_page_must_be_integer(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(TypeError):
            runtime.paginate(page=1.5)

    def test_boolean_is_not_a_valid_page(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(TypeError):
            runtime.paginate(page=True)

    def test_page_must_be_positive(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(ValueError):
            runtime.paginate(page=0)

    def test_page_size_must_be_integer(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(TypeError):
            runtime.paginate(page_size=2.5)

    def test_page_size_must_be_positive(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        with self.assertRaises(ValueError):
            runtime.paginate(page_size=0)

    def test_repr(self) -> None:
        runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.assertEqual(
            repr(runtime),
            (
                "EPList("
                "entity='company', "
                "rows=3, "
                "columns=3"
                ")"
            ),
        )


if __name__ == "__main__":
    unittest.main()