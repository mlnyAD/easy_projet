

import unittest

from django import forms

from framework.form import (
    FieldDefinition,
    FieldKind,
)
from framework.form.resolved_field import ResolvedField
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

    def test_resolved_checkbox_uses_checkbox_template(self):
        class DummyForm(forms.Form):
            is_active = forms.BooleanField(
                required=False,
            )

        django_form = DummyForm()

        resolved_field = ResolvedField(
            definition=FieldDefinition(
                name="is_active",
            ),
            bound_field=django_form["is_active"],
        )

        renderer = FieldRenderer()

        self.assertEqual(
            renderer.get_template_name(resolved_field),
            "edf/form/fields/checkbox.html",
        )


if __name__ == "__main__":
    unittest.main()