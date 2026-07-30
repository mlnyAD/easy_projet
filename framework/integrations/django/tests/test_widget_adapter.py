

import unittest

from django.forms import (
    CheckboxInput,
    FileInput,
    HiddenInput,
    PasswordInput,
    Select,
    TextInput,
    Textarea,
)

from framework.integrations.django.widget_adapter import WidgetAdapter


class WidgetAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = WidgetAdapter()

    def test_adapt_returns_same_widget_instance(self) -> None:
        widget = TextInput()

        adapted_widget = self.adapter.adapt(widget)

        self.assertIs(adapted_widget, widget)

    def test_adapt_rejects_non_widget_value(self) -> None:
        with self.assertRaises(TypeError):
            self.adapter.adapt("not-a-widget")  # type: ignore[arg-type]

    def test_text_input_receives_design_system_classes(self) -> None:
        widget = TextInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn("block", classes)
        self.assertIn("w-full", classes)
        self.assertIn("rounded-lg", classes)
        self.assertIn("border-gray-300", classes)

    def test_existing_classes_are_preserved(self) -> None:
        widget = TextInput(
            attrs={
                "class": "company-name-field custom-class",
            }
        )

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn("company-name-field", classes)
        self.assertIn("custom-class", classes)
        self.assertIn("w-full", classes)

    def test_classes_are_not_duplicated(self) -> None:
        widget = TextInput(
            attrs={
                "class": "block w-full",
            }
        )

        self.adapter.adapt(widget)
        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertEqual(classes.count("block"), 1)
        self.assertEqual(classes.count("w-full"), 1)

    def test_textarea_receives_rows_when_not_defined(self) -> None:
        widget = Textarea()

        self.adapter.adapt(widget)

        self.assertEqual(widget.attrs["rows"], 4)

    def test_textarea_preserves_existing_rows(self) -> None:
        widget = Textarea(
            attrs={
                "rows": 8,
            }
        )

        self.adapter.adapt(widget)

        self.assertEqual(widget.attrs["rows"], 8)

    def test_select_receives_select_classes(self) -> None:
        widget = Select()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn("w-full", classes)
        self.assertIn("pe-9", classes)

    def test_checkbox_receives_checkbox_classes(self) -> None:
        widget = CheckboxInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn("size-4", classes)
        self.assertIn("rounded", classes)
        self.assertNotIn("w-full", classes)

    def test_file_input_receives_file_classes(self) -> None:
        widget = FileInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn("w-full", classes)
        self.assertIn("file:px-4", classes)
        self.assertIn("hover:file:bg-gray-200", classes)

    def test_password_input_receives_default_autocomplete(self) -> None:
        widget = PasswordInput()

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["autocomplete"],
            "current-password",
        )

    def test_password_input_preserves_existing_autocomplete(self) -> None:
        widget = PasswordInput(
            attrs={
                "autocomplete": "new-password",
            }
        )

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["autocomplete"],
            "new-password",
        )

    def test_invalid_widget_receives_accessibility_attribute(self) -> None:
        widget = TextInput()

        self.adapter.adapt(widget, has_errors=True)

        self.assertEqual(widget.attrs["aria-invalid"], "true")

        classes = widget.attrs["class"].split()

        self.assertIn("border-red-500", classes)
        self.assertIn("focus:border-red-500", classes)

    def test_widget_without_errors_has_no_aria_invalid(self) -> None:
        widget = TextInput()

        self.adapter.adapt(widget, has_errors=False)

        self.assertNotIn("aria-invalid", widget.attrs)

    def test_described_by_is_added(self) -> None:
        widget = TextInput()

        self.adapter.adapt(
            widget,
            described_by="id_name_help",
        )

        self.assertEqual(
            widget.attrs["aria-describedby"],
            "id_name_help",
        )

    def test_existing_described_by_is_preserved_and_completed(self) -> None:
        widget = TextInput(
            attrs={
                "aria-describedby": "custom-description",
            }
        )

        self.adapter.adapt(
            widget,
            described_by="id_name_help",
        )

        described_by = widget.attrs["aria-describedby"].split()

        self.assertEqual(
            described_by,
            [
                "custom-description",
                "id_name_help",
            ],
        )

    def test_hidden_input_is_not_modified(self) -> None:
        widget = HiddenInput(
            attrs={
                "class": "existing-hidden-class",
            }
        )

        self.adapter.adapt(
            widget,
            has_errors=True,
            described_by="hidden-help",
        )

        self.assertEqual(
            widget.attrs,
            {
                "class": "existing-hidden-class",
            },
        )


if __name__ == "__main__":
    unittest.main()