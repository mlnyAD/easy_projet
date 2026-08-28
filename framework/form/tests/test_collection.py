

import unittest

from framework.form.collection import (
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
)


class FormCollectionColumnDefinitionTests(
    unittest.TestCase
):
    def test_minimal_definition(self) -> None:
        column = FormCollectionColumnDefinition(
            name="role",
        )

        self.assertEqual(
            column.name,
            "role",
        )
        self.assertIsNone(
            column.label,
        )
        self.assertIsNone(
            column.field_name,
        )
        self.assertTrue(
            column.visible,
        )
        self.assertEqual(
            column.align,
            "left",
        )
        self.assertEqual(
            column.width,
            "auto",
        )
        self.assertFalse(
            column.readonly,
        )

    def test_complete_definition(self) -> None:
        column = FormCollectionColumnDefinition(
            name="allocation",
            label="Taux de charge",
            field_name="allocation_percent",
            visible=True,
            align="center",
            width="sm",
            readonly=False,
        )

        self.assertEqual(
            column.name,
            "allocation",
        )
        self.assertEqual(
            column.label,
            "Taux de charge",
        )
        self.assertEqual(
            column.field_name,
            "allocation_percent",
        )
        self.assertEqual(
            column.align,
            "center",
        )
        self.assertEqual(
            column.width,
            "sm",
        )


class FormCollectionDefinitionTests(
    unittest.TestCase
):
    def test_minimal_definition(self) -> None:
        collection = FormCollectionDefinition(
            name="assignments",
            title="Personnel affecté",
        )

        self.assertEqual(
            collection.name,
            "assignments",
        )
        self.assertEqual(
            collection.title,
            "Personnel affecté",
        )
        self.assertIsNone(
            collection.description,
        )
        self.assertEqual(
            collection.columns,
            (),
        )
        self.assertTrue(
            collection.allow_add,
        )
        self.assertTrue(
            collection.allow_delete,
        )
        self.assertEqual(
            collection.add_label,
            "Ajouter",
        )
        self.assertEqual(
            collection.delete_label,
            "Supprimer",
        )
        self.assertTrue(
            collection.visible,
        )

    def test_definition_with_columns(self) -> None:
        role_column = FormCollectionColumnDefinition(
            name="role",
            label="Rôle",
            field_name="role",
        )

        active_column = FormCollectionColumnDefinition(
            name="active",
            label="Actif",
            field_name="is_active",
            align="center",
        )

        collection = FormCollectionDefinition(
            name="assignments",
            title="Personnel affecté",
            description=(
                "Personnes affectées à la tâche."
            ),
            columns=(
                role_column,
                active_column,
            ),
            add_label="Ajouter une personne",
        )

        self.assertEqual(
            collection.columns,
            (
                role_column,
                active_column,
            ),
        )
        self.assertEqual(
            collection.add_label,
            "Ajouter une personne",
        )