

import unittest

from framework.form import (
    FieldDefinition,
    FieldKind,
)
from framework.integrations.django.field_renderer import FieldRenderer


class FieldRendererTestCase(unittest.TestCase):
    """
    Tests du FieldRenderer.
    """

    def test_unknown_field_kind_returns_default_template(self):
        renderer = FieldRenderer()

        field = FieldDefinition(
            name="company",
            label="Société",
            kind=FieldKind.SELECT,
        )

        self.assertEqual(
            renderer.get_template_name(field),
            FieldRenderer.DEFAULT_TEMPLATE,
        )

    def test_known_field_kind_returns_registered_template(self):
        renderer = FieldRenderer()

        field = FieldDefinition(
            name="company",
            label="Société",
            kind=FieldKind.TEXT,
        )

        self.assertEqual(
            renderer.get_template_name(field),
            "edf/form/fields/text.html",
        )


if __name__ == "__main__":
    unittest.main()