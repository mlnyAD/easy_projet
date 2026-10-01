

import unittest

from framework.dictionary import EntityDefinition
from framework.list import ColumnDefinition, ListDefinition
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder


class ListViewModelBuilderVisibleColumnsTests(
    unittest.TestCase,
):
    def setUp(self):
        self.entity = EntityDefinition(
            {
                "entity": {
                    "name": "company",
                    "label": "Société",
                    "label_plural": "Sociétés",
                },
                "fields": {
                    "name": {
                        "label": "Nom",
                        "data_type": "string",
                        "required": True,
                        "max_length": 255,
                    },
                    "email": {
                        "label": "Adresse électronique",
                        "data_type": "email",
                        "required": False,
                        "max_length": 255,
                    },
                    "city": {
                        "label": "Ville",
                        "data_type": "string",
                        "required": False,
                        "max_length": 255,
                    },
                },
            }
        )

        self.definition = ListDefinition(
            identifier="test_company_list",
            entity=self.entity,
            columns=(
                ColumnDefinition(
                    field=self.entity.get_field("name"),
                    order=10,
                ),
                ColumnDefinition(
                    field=self.entity.get_field("email"),
                    order=20,
                ),
                ColumnDefinition(
                    field=self.entity.get_field("city"),
                    order=30,
                ),
            ),
            default_sort="name",
        )

        self.rows = (
            {
                "name": "AXCIO DATA",
                "email": "contact@axcio-data.fr",
                "city": "Paris",
            },
        )

        self.runtime = EPList(
            definition=self.definition,
            rows=self.rows,
        )

        self.page = ListPage(
            rows=self.rows,
            page=1,
            page_size=20,
            total_items=1,
            total_pages=1,
            has_previous=False,
            has_next=False,
        )

        self.builder = ListViewModelBuilder()

    def test_uses_default_visible_columns_when_not_provided(
        self,
    ):
        list_view = self.builder.build(
            runtime=self.runtime,
            page=self.page,
        )

        self.assertEqual(
            tuple(
                column.identifier
                for column in list_view.columns
            ),
            (
                "name",
                "email",
                "city",
            ),
        )

    def test_uses_selected_columns_in_definition_order(
        self,
    ):
        list_view = self.builder.build(
            runtime=self.runtime,
            page=self.page,
            visible_column_identifiers=(
                "city",
                "name",
            ),
        )

        self.assertEqual(
            tuple(
                column.identifier
                for column in list_view.columns
            ),
            (
                "name",
                "city",
            ),
        )

        self.assertEqual(
            len(list_view.rows[0].cells),
            2,
        )

    def test_rejects_unknown_visible_column(self):
        with self.assertRaisesRegex(
            ValueError,
            "n'existe pas",
        ):
            self.builder.build(
                runtime=self.runtime,
                page=self.page,
                visible_column_identifiers=(
                    "unknown",
                ),
            )

    def test_rejects_empty_visible_column_selection(self):
        with self.assertRaisesRegex(
            ValueError,
            "Au moins une colonne",
        ):
            self.builder.build(
                runtime=self.runtime,
                page=self.page,
                visible_column_identifiers=(),
            )


if __name__ == "__main__":
    unittest.main()