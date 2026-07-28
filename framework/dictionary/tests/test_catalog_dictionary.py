

import unittest

from common.dictionaries.catalog import (
    CATALOG_TYPE_DICTIONARY,
    CATALOG_VALUE_DICTIONARY,
)
from framework.dictionary.entity import EntityDefinition


class CatalogDictionaryTests(unittest.TestCase):

    def test_catalog_type_dictionary_is_valid(self):
        entity = EntityDefinition.from_dictionary(
            CATALOG_TYPE_DICTIONARY
        )

        self.assertEqual(entity.name, "catalog_type")
        self.assertEqual(entity.label, "Type de catalogue")
        self.assertEqual(entity.identifier_name, "id")

    def test_catalog_value_dictionary_is_valid(self) -> None:
        entity = EntityDefinition.from_dictionary(
            CATALOG_VALUE_DICTIONARY
        )

        self.assertEqual(entity.name, "catalog_value")
        self.assertEqual(entity.label, "Valeur de catalogue")
        self.assertEqual(entity.identifier_name, "id")
        self.assertTrue(entity.has_field("catalog_type"))
        self.assertTrue(entity.has_field("parent"))
    
if __name__ == "__main__":
    unittest.main()