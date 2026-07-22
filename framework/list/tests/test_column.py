

import unittest
from dataclasses import FrozenInstanceError

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition


class ColumnDefinitionTests(unittest.TestCase):
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
                    "name": {
                        "label": "Nom",
                        "data_type": "string",
                        "required": True,
                        "max_length": 150,
                    }
                },
            }
        )

        self.field = self.entity.get_field("name")

    def test_minimal_creation(self) -> None:
        column = ColumnDefinition(field=self.field)

        self.assertIs(column.field, self.field)

    def test_identifier_defaults_to_field_name(self) -> None:
        column = ColumnDefinition(field=self.field)

        self.assertEqual(column.identifier, "name")

    def test_custom_identifier(self) -> None:
        column = ColumnDefinition(
            field=self.field,
            identifier="company_name",
        )

        self.assertEqual(column.identifier, "company_name")

    def test_label_defaults_to_field_label(self) -> None:
        column = ColumnDefinition(field=self.field)

        self.assertEqual(column.label, "Nom")

    def test_custom_label(self) -> None:
        column = ColumnDefinition(
            field=self.field,
            label="Nom de la société",
        )

        self.assertEqual(column.label, "Nom de la société")

    def test_title_returns_effective_label(self) -> None:
        column = ColumnDefinition(
            field=self.field,
            label="Raison sociale",
        )

        self.assertEqual(column.title, "Raison sociale")

    def test_default_values(self) -> None:
        column = ColumnDefinition(field=self.field)

        self.assertTrue(column.visible)
        self.assertTrue(column.sortable)
        self.assertIsNone(column.width)
        self.assertEqual(column.order, 0)

    def test_complete_creation(self) -> None:
        column = ColumnDefinition(
            field=self.field,
            identifier="company_name",
            label="Société",
            visible=False,
            sortable=False,
            width=250,
            order=20,
        )

        self.assertEqual(column.identifier, "company_name")
        self.assertEqual(column.label, "Société")
        self.assertFalse(column.visible)
        self.assertFalse(column.sortable)
        self.assertEqual(column.width, 250)
        self.assertEqual(column.order, 20)

    def test_definition_is_immutable(self) -> None:
        column = ColumnDefinition(field=self.field)

        with self.assertRaises(FrozenInstanceError):
            column.label = "Autre libellé"

    def test_invalid_field_type(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(field="name")

    def test_invalid_identifier_type(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                identifier=123,
            )

    def test_empty_identifier(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                identifier="",
            )

    def test_blank_identifier(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                identifier="   ",
            )

    def test_invalid_label_type(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                label=123,
            )

    def test_empty_label(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                label="",
            )

    def test_blank_label(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                label="   ",
            )

    def test_invalid_visible_type(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                visible=1,
            )

    def test_invalid_sortable_type(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                sortable="yes",
            )

    def test_width_must_be_an_integer(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                width=100.5,
            )

    def test_boolean_is_not_a_valid_width(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                width=True,
            )

    def test_width_cannot_be_zero(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                width=0,
            )

    def test_width_cannot_be_negative(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                width=-100,
            )

    def test_order_must_be_an_integer(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                order=1.5,
            )

    def test_boolean_is_not_a_valid_order(self) -> None:
        with self.assertRaises(TypeError):
            ColumnDefinition(
                field=self.field,
                order=False,
            )

    def test_order_cannot_be_negative(self) -> None:
        with self.assertRaises(ValueError):
            ColumnDefinition(
                field=self.field,
                order=-1,
            )

    def test_repr(self) -> None:
        column = ColumnDefinition(
            field=self.field,
            identifier="company_name",
            label="Société",
        )

        self.assertEqual(
            repr(column),
            (
                "ColumnDefinition("
                "identifier='company_name', "
                "field='name', "
                "label='Société'"
                ")"
            ),
        )


if __name__ == "__main__":
    unittest.main()