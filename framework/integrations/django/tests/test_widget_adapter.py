

import unittest

from django import forms

from framework.integrations.django.widget_adapter import WidgetAdapter


class WidgetAdapterTests(unittest.TestCase):

    def test_adds_default_css_class(self):
        widget = forms.TextInput()

        WidgetAdapter().adapt(widget)

        self.assertIn(
            "edf-form-input",
            widget.attrs["class"],
        )

    def test_preserves_existing_classes(self):
        widget = forms.TextInput(
            attrs={
                "class": "custom-class",
            }
        )

        WidgetAdapter().adapt(widget)

        self.assertIn(
            "custom-class",
            widget.attrs["class"],
        )

        self.assertIn(
            "edf-form-input",
            widget.attrs["class"],
        )

    def test_does_not_duplicate_default_class(self):
        widget = forms.TextInput(
            attrs={
                "class": "edf-form-input",
            }
        )

        WidgetAdapter().adapt(widget)

        self.assertEqual(
            widget.attrs["class"].split().count("edf-form-input"),
            1,
        )


if __name__ == "__main__":
    unittest.main()