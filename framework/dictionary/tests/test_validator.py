

import unittest

from framework.dictionary.validator import (
    DictionaryValidationError,
    DictionaryValidator,
)


class DictionaryValidatorTests(unittest.TestCase):
    """Tests unitaires de DictionaryValidator."""

    def setUp(self) -> None:
        self.validator = DictionaryValidator()

    def make_valid_definition(self) -> dict:
        return {
            "entity": {
                "name": "company",
                "label": "Société",
                "label_plural": "Sociétés",
                "description": "Une société.",
            },
            "fields": {
                "id": {
                    "label": "Identifiant",
                    "data_type": "uuid",
                    "identifier": True,
                    "required": True,
                },
                "name": {
                    "label": "Nom",
                    "data_type": "string",
                    "required": True,
                    "unique": False,
                    "max_length": 150,
                },
            },
        }

    def test_accepts_valid_definition(self) -> None:
        self.validator.validate(self.make_valid_definition())

    def test_rejects_non_mapping_root(self) -> None:
        with self.assertRaisesRegex(
            DictionaryValidationError,
            "Le dictionnaire métier doit être une structure de type Mapping.",
        ):
            self.validator.validate([])  # type: ignore[arg-type]

    def test_rejects_missing_entity_section(self) -> None:
        definition = self.make_valid_definition()
        del definition["entity"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La section 'entity' est obligatoire.",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_fields_section(self) -> None:
        definition = self.make_valid_definition()
        del definition["fields"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La section 'fields' est obligatoire.",
        ):
            self.validator.validate(definition)

    def test_rejects_non_mapping_entity(self) -> None:
        definition = self.make_valid_definition()
        definition["entity"] = []  # type: ignore[assignment]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La section 'entity' doit être de type Mapping.",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_entity_name(self) -> None:
        definition = self.make_valid_definition()
        del definition["entity"]["name"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "entity.name",
        ):
            self.validator.validate(definition)

    def test_rejects_empty_entity_name(self) -> None:
        definition = self.make_valid_definition()
        definition["entity"]["name"] = "   "

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "entity.name",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_entity_label(self) -> None:
        definition = self.make_valid_definition()
        del definition["entity"]["label"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "entity.label",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_entity_plural_label(self) -> None:
        definition = self.make_valid_definition()
        del definition["entity"]["label_plural"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "entity.label_plural",
        ):
            self.validator.validate(definition)

    def test_rejects_non_string_entity_description(self) -> None:
        definition = self.make_valid_definition()
        definition["entity"]["description"] = 123

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "entity.description",
        ):
            self.validator.validate(definition)

    def test_accepts_missing_entity_description(self) -> None:
        definition = self.make_valid_definition()
        del definition["entity"]["description"]

        self.validator.validate(definition)

    def test_rejects_non_mapping_fields(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"] = []  # type: ignore[assignment]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La section 'fields' doit être de type Mapping.",
        ):
            self.validator.validate(definition)

    def test_rejects_empty_fields(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"] = {}

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "doit contenir au moins un champ",
        ):
            self.validator.validate(definition)

    def test_rejects_empty_field_name(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"][""] = definition["fields"].pop("name")

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "Chaque nom de champ doit être une chaîne non vide.",
        ):
            self.validator.validate(definition)

    def test_rejects_non_mapping_field_definition(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"] = []  # type: ignore[assignment]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "Le champ 'name' doit être défini par un Mapping.",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_field_label(self) -> None:
        definition = self.make_valid_definition()
        del definition["fields"]["name"]["label"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "Le champ 'name' doit posséder un label non vide.",
        ):
            self.validator.validate(definition)

    def test_rejects_empty_field_label(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["label"] = " "

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "Le champ 'name' doit posséder un label non vide.",
        ):
            self.validator.validate(definition)

    def test_rejects_unknown_data_type(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["data_type"] = "unknown"

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "utilise un type inconnu",
        ):
            self.validator.validate(definition)

    def test_rejects_missing_data_type(self) -> None:
        definition = self.make_valid_definition()
        del definition["fields"]["name"]["data_type"]

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "utilise un type inconnu",
        ):
            self.validator.validate(definition)

    def test_rejects_non_string_field_description(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["description"] = 123

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La description du champ 'name' doit être une chaîne.",
        ):
            self.validator.validate(definition)

    def test_accepts_missing_field_description(self) -> None:
        definition = self.make_valid_definition()

        self.validator.validate(definition)

    def test_rejects_zero_max_length(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["max_length"] = 0

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "max_length invalide",
        ):
            self.validator.validate(definition)

    def test_rejects_negative_max_length(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["max_length"] = -1

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "max_length invalide",
        ):
            self.validator.validate(definition)

    def test_rejects_non_integer_max_length(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["max_length"] = "150"

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "max_length invalide",
        ):
            self.validator.validate(definition)

    def test_rejects_boolean_max_length(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["max_length"] = True

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "max_length invalide",
        ):
            self.validator.validate(definition)

    def test_accepts_missing_max_length(self) -> None:
        definition = self.make_valid_definition()
        del definition["fields"]["name"]["max_length"]

        self.validator.validate(definition)

    def test_rejects_non_boolean_identifier(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["id"]["identifier"] = "yes"

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La propriété 'identifier'.*doit être un booléen",
        ):
            self.validator.validate(definition)

    def test_rejects_non_boolean_required(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["required"] = 1

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La propriété 'required'.*doit être un booléen",
        ):
            self.validator.validate(definition)

    def test_rejects_non_boolean_unique(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["unique"] = "false"

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "La propriété 'unique'.*doit être un booléen",
        ):
            self.validator.validate(definition)

    def test_accepts_missing_boolean_properties(self) -> None:
        definition = self.make_valid_definition()
        del definition["fields"]["name"]["required"]
        del definition["fields"]["name"]["unique"]

        self.validator.validate(definition)

    def test_rejects_missing_identifier(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["id"]["identifier"] = False

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "exactement un champ identifiant",
        ):
            self.validator.validate(definition)

    def test_rejects_multiple_identifiers(self) -> None:
        definition = self.make_valid_definition()
        definition["fields"]["name"]["identifier"] = True

        with self.assertRaisesRegex(
            DictionaryValidationError,
            "exactement un champ identifiant",
        ):
            self.validator.validate(definition)


if __name__ == "__main__":
    unittest.main()