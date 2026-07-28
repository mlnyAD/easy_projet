

import unittest
from types import MappingProxyType

from framework.dictionary.entity import EntityDefinition
from framework.dictionary.field import FieldDefinition
from framework.dictionary.validator import DictionaryValidationError


class EntityDefinitionTests(unittest.TestCase):
    """Tests unitaires de EntityDefinition."""

    def setUp(self) -> None:
        self.definition = {
            "entity": {
                "name": "company",
                "label": "Société",
                "label_plural": "Sociétés",
                "description": "Entreprise intervenant dans Easy Projet.",
            },
            "fields": {
                "id": {
                    "label": "Identifiant",
                    "data_type": "uuid",
                    "identifier": True,
                    "required": True,
                },
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
            },
        }

        self.entity = EntityDefinition(self.definition)

    def test_exposes_entity_name(self) -> None:
        self.assertEqual(self.entity.name, "company")

    def test_exposes_entity_label(self) -> None:
        self.assertEqual(self.entity.label, "Société")

    def test_exposes_entity_plural_label(self) -> None:
        self.assertEqual(self.entity.label_plural, "Sociétés")

    def test_exposes_entity_description(self) -> None:
        self.assertEqual(
            self.entity.description,
            "Entreprise intervenant dans Easy Projet.",
        )

    def test_description_defaults_to_empty_string(self) -> None:
        definition = {
            "entity": {
                "name": "project",
                "label": "Projet",
                "label_plural": "Projets",
            },
            "fields": {
                "id": {
                    "label": "Identifiant",
                    "data_type": "uuid",
                    "identifier": True,
                },
            },
        }

        entity = EntityDefinition(definition)

        self.assertEqual(entity.description, "")

    def test_fields_are_field_definitions(self) -> None:
        self.assertIsInstance(
            self.entity.fields["code"],
            FieldDefinition,
        )

    def test_fields_mapping_is_read_only(self) -> None:
        self.assertIsInstance(
            self.entity.fields,
            MappingProxyType,
        )

        with self.assertRaises(TypeError):
            self.entity.fields["other"] = self.entity.fields["code"]  # type: ignore[index]

    def test_field_names_preserve_declaration_order(self) -> None:
        self.assertEqual(
            self.entity.field_names,
            ("id", "code", "name"),
        )

    def test_get_field_returns_field_definition(self) -> None:
        field = self.entity.get_field("code")

        self.assertIsInstance(field, FieldDefinition)
        self.assertEqual(field.name, "code")
        self.assertEqual(field.label, "Code")
        self.assertEqual(field.data_type, "string")
        self.assertEqual(field.max_length, 10)

    def test_get_field_raises_explicit_key_error(self) -> None:
        with self.assertRaisesRegex(
            KeyError,
            "Le champ 'unknown' n'existe pas dans l'entité 'company'.",
        ):
            self.entity.get_field("unknown")

    def test_has_field_returns_true_for_existing_field(self) -> None:
        self.assertTrue(self.entity.has_field("name"))

    def test_has_field_returns_false_for_unknown_field(self) -> None:
        self.assertFalse(self.entity.has_field("unknown"))

    def test_identifier_name_returns_identifier_field_name(self) -> None:
        self.assertEqual(self.entity.identifier_name, "id")

    def test_identifier_returns_field_definition(self) -> None:
        identifier = self.entity.identifier

        self.assertIsInstance(identifier, FieldDefinition)
        self.assertEqual(identifier.name, "id")
        self.assertTrue(identifier.identifier)

    def test_identifier_returns_none_when_missing(self) -> None:
        definition = {
            "entity": {
                "name": "company",
                "label": "Société",
                "label_plural": "Sociétés",
            },
            "fields": {
                "name": {
                    "label": "Nom",
                    "data_type": "string",
                },
            },
        }

        entity = EntityDefinition(definition)

        self.assertIsNone(entity.identifier_name)
        self.assertIsNone(entity.identifier)

    def test_entity_is_iterable(self) -> None:
        field_names = tuple(field.name for field in self.entity)

        self.assertEqual(
            field_names,
            ("id", "code", "name"),
        )

    def test_len_returns_field_count(self) -> None:
        self.assertEqual(len(self.entity), 3)

    def test_contains_checks_field_name(self) -> None:
        self.assertIn("code", self.entity)
        self.assertNotIn("unknown", self.entity)

    def test_repr_contains_name_and_field_count(self) -> None:
        self.assertEqual(
            repr(self.entity),
            "EntityDefinition(name='company', fields=3)",
        )

    def test_from_dictionary_returns_entity_definition(self):
        entity = EntityDefinition.from_dictionary(self.definition)

        self.assertIsInstance(entity, EntityDefinition)
        self.assertEqual(entity.name, "company")

    def test_from_dictionary_validates_dictionary(self):
        definition = {
            "entity": {},
            "fields": {},
        }

        with self.assertRaises(DictionaryValidationError):
            EntityDefinition.from_dictionary(definition)

if __name__ == "__main__":
    unittest.main()