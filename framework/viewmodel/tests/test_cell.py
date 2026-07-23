

import unittest

from framework.dictionary import EntityDefinition
from framework.list import ColumnDefinition
from framework.viewmodel.cell import ViewCell
from framework.viewmodel.column import ViewColumn


COMPANY_DICTIONARY = {
    "entity": {
        "name": "company",
        "label": "Société",
        "label_plural": "Sociétés",
    },
    "fields": {
        "email": {
            "label": "Adresse électronique",
            "data_type": "email",
            "required": True,
            "max_length": 254,
        },
    },
}


class ViewCellTests(unittest.TestCase):

    def setUp(self) -> None:
        entity = EntityDefinition(COMPANY_DICTIONARY)

        column_definition = ColumnDefinition(
            field=entity.get_field("email"),
            order=10,
        )

        view_column = ViewColumn(
            definition=column_definition,
        )

        self.cell = ViewCell(
            value="contact@entreprise.fr",
            display_value="contact@entreprise.fr",
            column=view_column,
        )

    def test_identifier_returns_column_identifier(self) -> None:
        self.assertEqual(
            self.cell.identifier,
            "email",
        )

    def test_label_returns_column_label(self) -> None:
        self.assertEqual(
            self.cell.label,
            "Adresse électronique",
        )

    def test_data_type_returns_field_data_type(self) -> None:
        self.assertEqual(
            self.cell.data_type,
            "email",
        )

    def test_sortable_returns_column_sortable_state(self) -> None:
        self.assertEqual(
            self.cell.sortable,
            self.cell.column.sortable,
        )

    def test_visible_returns_column_visibility_state(self) -> None:
        self.assertEqual(
            self.cell.visible,
            self.cell.column.visible,
        )


if __name__ == "__main__":
    unittest.main()