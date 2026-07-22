

import unittest
from types import MappingProxyType

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition
from framework.list.definition import DEFAULT_PAGE_SIZE, ListDefinition


class ListDefinitionTests(unittest.TestCase):
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
            order=10,
        )
        self.name_column = ColumnDefinition(
            field=self.entity.get_field("name"),
            width=250,
            order=20,
        )
        self.city_column = ColumnDefinition(
            field=self.entity.get_field("city"),
            visible=False,
            order=30,
        )

        self.columns = [
            self.code_column,
            self.name_column,
            self.city_column,
        ]

    def test_minimal_creation(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=[self.name_column],
        )

        self.assertIs(definition.entity, self.entity)
        self.assertEqual(
            definition.columns,
            (self.name_column,),
        )

    def test_complete_creation(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
            default_sort="name",
            page_size=50,
        )

        self.assertIs(definition.entity, self.entity)
        self.assertEqual(
            definition.columns,
            tuple(self.columns),
        )
        self.assertEqual(definition.default_sort, "name")
        self.assertEqual(definition.page_size, 50)

    def test_default_values(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=[self.name_column],
        )

        self.assertIsNone(definition.default_sort)
        self.assertEqual(
            definition.page_size,
            DEFAULT_PAGE_SIZE,
        )

    def test_columns_are_stored_as_tuple(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertIsInstance(definition.columns, tuple)

    def test_source_columns_can_change_without_affecting_definition(
        self,
    ) -> None:
        source_columns = [self.code_column]

        definition = ListDefinition(
            entity=self.entity,
            columns=source_columns,
        )

        source_columns.append(self.name_column)

        self.assertEqual(
            definition.columns,
            (self.code_column,),
        )

    def test_columns_by_identifier_is_read_only(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertIsInstance(
            definition.columns_by_identifier,
            MappingProxyType,
        )

        with self.assertRaises(TypeError):
            definition.columns_by_identifier["other"] = self.name_column

    def test_columns_by_identifier(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertIs(
            definition.columns_by_identifier["code"],
            self.code_column,
        )
        self.assertIs(
            definition.columns_by_identifier["name"],
            self.name_column,
        )
        self.assertIs(
            definition.columns_by_identifier["city"],
            self.city_column,
        )

    def test_column_identifiers(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertEqual(
            definition.column_identifiers,
            ("code", "name", "city"),
        )

    def test_visible_columns(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertEqual(
            definition.visible_columns,
            (
                self.code_column,
                self.name_column,
            ),
        )

    def test_has_column_returns_true(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertTrue(definition.has_column("name"))

    def test_has_column_returns_false(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertFalse(definition.has_column("email"))

    def test_get_column(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertIs(
            definition.get_column("name"),
            self.name_column,
        )

    def test_get_unknown_column_raises_key_error(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        with self.assertRaises(KeyError):
            definition.get_column("unknown")

    def test_iteration(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertEqual(
            list(definition),
            self.columns,
        )

    def test_len(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertEqual(len(definition), 3)

    def test_contains_existing_identifier(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertIn("name", definition)

    def test_contains_unknown_identifier(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
        )

        self.assertNotIn("email", definition)

    def test_invalid_entity_type(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity="company",
                columns=[self.name_column],
            )

    def test_columns_must_be_a_sequence(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns=123,
            )

    def test_columns_cannot_be_a_string(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns="name",
            )

    def test_columns_cannot_be_empty(self) -> None:
        with self.assertRaises(ValueError):
            ListDefinition(
                entity=self.entity,
                columns=[],
            )

    def test_each_column_must_be_a_column_definition(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns=[
                    self.name_column,
                    "city",
                ],
            )

    def test_default_sort_must_be_a_string(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                default_sort=123,
            )

    def test_default_sort_cannot_be_empty(self) -> None:
        with self.assertRaises(ValueError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                default_sort="",
            )

    def test_default_sort_cannot_be_blank(self) -> None:
        with self.assertRaises(ValueError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                default_sort="   ",
            )

    def test_page_size_must_be_an_integer(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                page_size=20.5,
            )

    def test_boolean_is_not_a_valid_page_size(self) -> None:
        with self.assertRaises(TypeError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                page_size=True,
            )

    def test_page_size_cannot_be_zero(self) -> None:
        with self.assertRaises(ValueError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                page_size=0,
            )

    def test_page_size_cannot_be_negative(self) -> None:
        with self.assertRaises(ValueError):
            ListDefinition(
                entity=self.entity,
                columns=self.columns,
                page_size=-20,
            )

    def test_repr(self) -> None:
        definition = ListDefinition(
            entity=self.entity,
            columns=self.columns,
            default_sort="name",
            page_size=50,
        )

        self.assertEqual(
            repr(definition),
            (
                "ListDefinition("
                "entity='company', "
                "columns=3, "
                "default_sort='name', "
                "page_size=50"
                ")"
            ),
        )


if __name__ == "__main__":
    unittest.main()