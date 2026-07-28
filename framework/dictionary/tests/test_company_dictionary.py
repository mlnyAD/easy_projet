

import unittest

from common.dictionaries.company import COMPANY_DICTIONARY
from framework.dictionary.entity import EntityDefinition


class CompanyDictionaryTests(unittest.TestCase):
    """Tests du dictionnaire métier Company."""

    def test_company_dictionary_is_valid(self) -> None:
        entity = EntityDefinition.from_dictionary(
            COMPANY_DICTIONARY
        )

        self.assertEqual(entity.name, "company")
        self.assertEqual(entity.label, "Société")
        self.assertEqual(entity.label_plural, "Sociétés")
        self.assertEqual(entity.identifier_name, "id")

    def test_company_dictionary_contains_expected_fields(self) -> None:
        entity = EntityDefinition.from_dictionary(
            COMPANY_DICTIONARY
        )

        expected_fields = {
            "id",
            "name",
            "siret",
            "vat_number",
            "email",
            "phone",
            "address_1",
            "address_2",
            "address_3",
            "postal_code",
            "city",
            "country",
            "is_active",
            "created_at",
            "updated_at",
        }

        self.assertEqual(
            set(entity.fields),
            expected_fields,
        )


if __name__ == "__main__":
    unittest.main()