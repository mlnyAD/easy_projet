

import unittest

from django import forms

from framework.form.collection import (
    FormCollectionColumnDefinition,
)
from framework.form.resolved_collection_cell import (
    ResolvedFormCollectionCell,
)
from framework.form.resolved_collection_row import (
    ResolvedFormCollectionRow,
)


class SampleForm(forms.Form):
    name = forms.CharField()
    DELETE = forms.BooleanField(
        required=False,
    )


class ResolvedFormCollectionCellTests(
    unittest.TestCase
):
    def test_editable_cell(self):
        form = SampleForm()

        definition = (
            FormCollectionColumnDefinition(
                name="name",
                label="Nom",
                field_name="name",
            )
        )

        cell = ResolvedFormCollectionCell(
            definition=definition,
            bound_field=form["name"],
        )

        self.assertEqual(
            cell.name,
            "name",
        )
        self.assertEqual(
            cell.label,
            "Nom",
        )
        self.assertTrue(
            cell.editable,
        )
        self.assertEqual(
            list(cell.errors),
            [],
        )

    def test_display_cell(self):
        definition = (
            FormCollectionColumnDefinition(
                name="company",
                label="Société",
                readonly=True,
            )
        )

        cell = ResolvedFormCollectionCell(
            definition=definition,
            display_value="AXCIO-DATA",
        )

        self.assertFalse(
            cell.editable,
        )
        self.assertEqual(
            cell.display_value,
            "AXCIO-DATA",
        )
        self.assertEqual(
            cell.errors,
            (),
        )


class ResolvedFormCollectionRowTests(
    unittest.TestCase
):
    def test_row_contains_cells(self):
        form = SampleForm()

        cell = ResolvedFormCollectionCell(
            definition=(
                FormCollectionColumnDefinition(
                    name="name",
                    field_name="name",
                )
            ),
            bound_field=form["name"],
        )

        row = ResolvedFormCollectionRow(
            django_form=form,
            cells=[cell],
        )

        self.assertEqual(
            len(row.cells),
            1,
        )
        self.assertIs(
            row.cells[0],
            cell,
        )

    def test_delete_field(self):
        form = SampleForm()

        row = ResolvedFormCollectionRow(
            django_form=form,
        )

        self.assertIsNotNone(
            row.delete_field,
        )

    def test_delete_field_is_none_when_missing(self):
        class FormWithoutDelete(forms.Form):
            name = forms.CharField()

        row = ResolvedFormCollectionRow(
            django_form=FormWithoutDelete(),
        )

        self.assertIsNone(
            row.delete_field,
        )