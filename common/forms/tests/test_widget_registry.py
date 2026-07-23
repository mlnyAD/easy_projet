

"""
Tests du registre des widgets Easy Projet.
"""

from django import forms
from django.test import SimpleTestCase

from common.forms.widget_registry import (
    get_widget_kind,
    validate_bound_field,
)
from common.forms.widgets import TelInput


class TestForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(),
    )

    phone = forms.CharField(
        widget=TelInput(),
    )

    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
    )

    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(),
    )

    country = forms.ChoiceField(
        choices=(
            ("FR", "France"),
            ("BE", "Belgique"),
        ),
        widget=forms.Select(),
    )

    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(),
    )


class WidgetRegistryTests(SimpleTestCase):
    def setUp(self):
        self.form = TestForm()

    def test_text_input_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["name"]),
            "text",
        )

    def test_email_input_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["email"]),
            "email",
        )

    def test_phone_input_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["phone"]),
            "phone",
        )

    def test_checkbox_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["is_active"]),
            "checkbox",
        )

    def test_textarea_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["notes"]),
            "textarea",
        )

    def test_select_is_identified(self):
        self.assertEqual(
            get_widget_kind(self.form["country"]),
            "select",
        )

    def test_unknown_widget_uses_default_kind(self):
        self.assertEqual(
            get_widget_kind(self.form["attachment"]),
            "default",
        )

    def test_validate_bound_field_rejects_invalid_value(self):
        with self.assertRaises(TypeError):
            validate_bound_field("name")