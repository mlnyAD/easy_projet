

import unittest
from dataclasses import FrozenInstanceError

from framework.dictionary.field import FieldDefinition


class FieldDefinitionTests(unittest.TestCase):
    """Tests unitaires de FieldDefinition."""

    def setUp(self) -> None:
        self.source_definition = {
            "label": "Nom",
            "data_type": "string",
            "description": "Nom de la société.",
            "required": True,
            "identifier": False,
            "unique": True,
            "max_length": 150,
            "default": "",
        }

        self.field = FieldDefinition(
            name="name",
            definition=self.source_definition,
        )

    def test_exposes_field_name(self) -> None:
        self.assertEqual(self.field.name, "name")

    def test_exposes_required_properties(self) -> None:
        self.assertEqual(self.field.label, "Nom")
        self.assertEqual(self.field.data_type, "string")

    def test_exposes_optional_properties(self) -> None:
        self.assertEqual(
            self.field.description,
            "Nom de la société.",
        )
        self.assertTrue(self.field.required)
        self.assertFalse(self.field.identifier)
        self.assertTrue(self.field.unique)
        self.assertEqual(self.field.max_length, 150)
        self.assertEqual(self.field.default, "")

    def test_uses_defaults_for_missing_optional_properties(self) -> None:
        field = FieldDefinition(
            name="email",
            definition={
                "label": "Adresse électronique",
                "data_type": "email",
            },
        )

        self.assertEqual(field.description, "")
        self.assertFalse(field.required)
        self.assertFalse(field.identifier)
        self.assertFalse(field.unique)
        self.assertIsNone(field.max_length)
        self.assertIsNone(field.default)

    def test_get_returns_additional_property(self) -> None:
        field = FieldDefinition(
            name="status",
            definition={
                "label": "Statut",
                "data_type": "string",
                "catalog": "company_status",
            },
        )

        self.assertEqual(
            field.get("catalog"),
            "company_status",
        )

    def test_get_returns_default_for_unknown_property(self) -> None:
        self.assertEqual(
            self.field.get("unknown", "fallback"),
            "fallback",
        )

    def test_instance_is_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.field.name = "other"  # type: ignore[misc]

    def test_definition_is_read_only(self) -> None:
        with self.assertRaises(TypeError):
            self.field.definition["label"] = "Autre"  # type: ignore[index]

    def test_source_mapping_is_copied(self) -> None:
        self.source_definition["label"] = "Libellé modifié"

        self.assertEqual(self.field.label, "Nom")

    def test_repr_contains_name_and_data_type(self) -> None:
        self.assertEqual(
            repr(self.field),
            "FieldDefinition(name='name', data_type='string')",
        )


if __name__ == "__main__":
    unittest.main()