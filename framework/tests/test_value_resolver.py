

import unittest

from framework.value_resolver import (
    ValueResolutionError,
    resolve_value,
)


class ValueResolverTests(unittest.TestCase):
    def test_resolve_mapping_value(self):
        source = {
            "name": "AXCIO-DATA",
        }

        self.assertEqual(
            resolve_value(
                source,
                "name",
            ),
            "AXCIO-DATA",
        )

    def test_resolve_object_value(self):
        class Source:
            name = "AXCIO-DATA"

        self.assertEqual(
            resolve_value(
                Source(),
                "name",
            ),
            "AXCIO-DATA",
        )

    def test_resolve_nested_object_value(self):
        class Company:
            name = "AXCIO-DATA"

        class User:
            company = Company()

        class Assignment:
            user = User()

        self.assertEqual(
            resolve_value(
                Assignment(),
                "user.company.name",
            ),
            "AXCIO-DATA",
        )

    def test_resolve_nested_mapping_value(self):
        source = {
            "user": {
                "company": {
                    "name": "AXCIO-DATA",
                },
            },
        }

        self.assertEqual(
            resolve_value(
                source,
                "user.company.name",
            ),
            "AXCIO-DATA",
        )

    def test_missing_mapping_value_raises_error(self):
        with self.assertRaisesRegex(
            ValueResolutionError,
            "unknown",
        ):
            resolve_value(
                {},
                "unknown",
            )

    def test_missing_object_attribute_raises_error(self):
        class Source:
            pass

        with self.assertRaisesRegex(
            ValueResolutionError,
            "unknown",
        ):
            resolve_value(
                Source(),
                "unknown",
            )

    def test_name_must_be_string(self):
        with self.assertRaises(TypeError):
            resolve_value(
                {},
                123,
            )

    def test_name_cannot_be_empty(self):
        with self.assertRaises(ValueError):
            resolve_value(
                {},
                "",
            )