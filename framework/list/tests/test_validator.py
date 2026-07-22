

import unittest

from framework.dictionary.entity import EntityDefinition
from framework.list.column import ColumnDefinition
from framework.list.definition import ListDefinition
from framework.list.validator import (
    ListValidationError,
    ListValidator,
)


class ListValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ListValidator()

        self.company_entity = EntityDefinition(
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

        self.project_entity = EntityDefinition(
            {
                "entity": {
                    "name": "project",
                    "label": "Projet",
                    "label_plural": "Projets",
                    "description": "Projet géré dans Easy Projet.",
                },
                "fields": {
                    "name": {
                        "label": "Nom",
                        "data_type": "string",
                        "required": True,
                        "max_length": 150,
                    },
                    "status": {
                        "label": "État",
                        "data_type": "string",
                        "required": True,
                        "max_length": 30,
                    },
                },
            }
        )

        self.code_column = ColumnDefinition(
            field=self.company_entity.get_field("code"),
        )

        self.name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
        )

        self.city_column = ColumnDefinition(
            field=self.company_entity.get_field("city"),
        )

    def test_valid_definition(self) -> None:
        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                self.name_column,
                self.city_column,
            ],
            default_sort="name",
        )

        self.validator.validate(definition)

    def test_valid_definition_without_default_sort(self) -> None:
        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                self.name_column,
            ],
        )

        self.validator.validate(definition)

    def test_validate_returns_none(self) -> None:
        definition = ListDefinition(
            entity=self.company_entity,
            columns=[self.name_column],
        )

        result = self.validator.validate(definition)

        self.assertIsNone(result)

    def test_definition_must_be_a_list_definition(self) -> None:
        with self.assertRaises(TypeError):
            self.validator.validate("company")

    def test_duplicate_identifiers_are_rejected(self) -> None:
        first_column = ColumnDefinition(
            field=self.company_entity.get_field("code"),
            identifier="main",
        )

        second_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            identifier="main",
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                first_column,
                second_column,
            ],
        )

        with self.assertRaisesRegex(
            ListValidationError,
            "'main' est déclaré plusieurs fois",
        ):
            self.validator.validate(definition)

    def test_field_unknown_to_entity_is_rejected(self) -> None:
        project_status_column = ColumnDefinition(
            field=self.project_entity.get_field("status"),
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.name_column,
                project_status_column,
            ],
        )

        with self.assertRaisesRegex(
            ListValidationError,
            "champ inconnu 'status'",
        ):
            self.validator.validate(definition)

    def test_field_from_another_entity_is_rejected_even_with_same_name(
        self,
    ) -> None:
        project_name_column = ColumnDefinition(
            field=self.project_entity.get_field("name"),
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[project_name_column],
        )

        with self.assertRaisesRegex(
            ListValidationError,
            "ne référence pas le FieldDefinition appartenant",
        ):
            self.validator.validate(definition)

    def test_default_sort_must_reference_an_existing_column(self) -> None:
        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                self.name_column,
            ],
            default_sort="city",
        )

        with self.assertRaisesRegex(
            ListValidationError,
            "'city' n'existe pas dans la liste",
        ):
            self.validator.validate(definition)

    def test_default_sort_column_must_be_sortable(self) -> None:
        non_sortable_name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            sortable=False,
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                non_sortable_name_column,
            ],
            default_sort="name",
        )

        with self.assertRaisesRegex(
            ListValidationError,
            "'name' n'est pas triable",
        ):
            self.validator.validate(definition)

    def test_hidden_column_can_be_used_as_default_sort(self) -> None:
        hidden_name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            visible=False,
            sortable=True,
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                hidden_name_column,
            ],
            default_sort="name",
        )

        self.validator.validate(definition)

    def test_multiple_columns_can_have_default_order(self) -> None:
        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                self.name_column,
                self.city_column,
            ],
        )

        self.assertEqual(
            [column.order for column in definition.columns],
            [0, 0, 0],
        )

        self.validator.validate(definition)

    def test_custom_identifier_can_be_default_sort(self) -> None:
        company_name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            identifier="company_name",
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                self.code_column,
                company_name_column,
            ],
            default_sort="company_name",
        )

        self.validator.validate(definition)

    def test_duplicate_fields_are_allowed_with_distinct_identifiers(
        self,
    ) -> None:
        short_name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            identifier="short_name",
            label="Nom",
        )

        full_name_column = ColumnDefinition(
            field=self.company_entity.get_field("name"),
            identifier="full_name",
            label="Raison sociale",
        )

        definition = ListDefinition(
            entity=self.company_entity,
            columns=[
                short_name_column,
                full_name_column,
            ],
        )

        self.validator.validate(definition)


if __name__ == "__main__":
    unittest.main()