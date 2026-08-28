

from django import forms
from django.forms import formset_factory
from django.test import SimpleTestCase

from framework.form.collection import (
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
)
from framework.form.resolved_collection import (
    ResolvedFormCollection,
)


class AssignmentForm(forms.Form):
    role = forms.CharField()
    allocation = forms.IntegerField()


class Company:
    def __init__(self, name):
        self.name = name


class User:
    def __init__(self, name, company):
        self.name = name
        self.company = company


class Assignment:
    def __init__(self, user):
        self.user = user


class AssignmentModelLikeForm(forms.Form):
    """
    Formulaire de test portant artificiellement une instance.

    Cela permet de tester le mécanisme générique de résolution
    sans introduire de modèle métier Django dans les tests
    du framework.
    """

    role = forms.CharField()

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance


class ResolvedFormCollectionTests(SimpleTestCase):
    def test_rows_resolve_editable_field(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=1,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    label="Rôle",
                    field_name="role",
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        rows = collection.rows

        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0].cells), 1)

        cell = rows[0].cells[0]

        self.assertEqual(cell.name, "role")
        self.assertEqual(cell.label, "Rôle")
        self.assertEqual(cell.bound_field.name, "role")
        self.assertTrue(cell.editable)

    def test_rows_resolve_display_value(self):
        company = Company("AXCIO-DATA")
        user = User(
            name="Jean Dupont",
            company=company,
        )
        assignment = Assignment(user)

        formset_class = formset_factory(
            AssignmentModelLikeForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        django_form = AssignmentModelLikeForm(
            instance=assignment,
        )
        formset.forms.append(django_form)

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="user",
                    label="Utilisateur",
                    source_name="user.name",
                    readonly=True,
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        cell = collection.rows[0].cells[0]

        self.assertIsNone(cell.bound_field)
        self.assertEqual(
            cell.display_value,
            "Jean Dupont",
        )
        self.assertFalse(cell.editable)

    def test_rows_resolve_nested_display_value(self):
        company = Company("AXCIO-DATA")
        user = User(
            name="Jean Dupont",
            company=company,
        )
        assignment = Assignment(user)

        formset_class = formset_factory(
            AssignmentModelLikeForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        django_form = AssignmentModelLikeForm(
            instance=assignment,
        )
        formset.forms.append(django_form)

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="company",
                    label="Société",
                    source_name="user.company.name",
                    readonly=True,
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        cell = collection.rows[0].cells[0]

        self.assertEqual(
            cell.display_value,
            "AXCIO-DATA",
        )

    def test_rows_ignore_invisible_column(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=1,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    field_name="role",
                ),
                FormCollectionColumnDefinition(
                    name="allocation",
                    field_name="allocation",
                    visible=False,
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        cells = collection.rows[0].cells

        self.assertEqual(len(cells), 1)
        self.assertEqual(
            cells[0].name,
            "role",
        )

    def test_unknown_django_field_raises_error(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=1,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="unknown",
                    field_name="unknown",
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        with self.assertRaisesRegex(
            ValueError,
            "unknown",
        ):
            collection.rows

    def test_column_without_source_raises_error(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=1,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        with self.assertRaisesRegex(
            ValueError,
            "field_name.*source_name",
        ):
            collection.rows
        
    def test_empty_row_resolves_editable_field(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    label="Rôle",
                    field_name="role",
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        row = collection.empty_row

        self.assertEqual(len(row.cells), 1)
        self.assertEqual(
            row.cells[0].bound_field.name,
            "role",
        )
        self.assertTrue(
            row.cells[0].editable,
        )


    def test_empty_row_does_not_resolve_display_value(self):
        formset_class = formset_factory(
            AssignmentModelLikeForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="company",
                    label="Société",
                    source_name="user.company.name",
                    readonly=True,
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        cell = collection.empty_row.cells[0]

        self.assertIsNone(cell.bound_field)
        self.assertIsNone(cell.display_value)
        self.assertFalse(cell.editable)


    def test_empty_row_ignores_invisible_column(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    field_name="role",
                ),
                FormCollectionColumnDefinition(
                    name="allocation",
                    field_name="allocation",
                    visible=False,
                ),
            ),
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        cells = collection.empty_row.cells

        self.assertEqual(len(cells), 1)
        self.assertEqual(
            cells[0].name,
            "role",
        )
        
    def test_allow_delete_requires_deletable_formset(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=0,
            can_delete=False,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    field_name="role",
                ),
            ),
            allow_delete=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "can_delete=True",
        ):
            ResolvedFormCollection(
                definition=definition,
                formset=formset,
            )


    def test_deletable_formset_accepts_hidden_delete_capability(self):
        formset_class = formset_factory(
            AssignmentForm,
            extra=0,
            can_delete=True,
        )
        formset = formset_class()

        definition = FormCollectionDefinition(
            name="assignments",
            title="Personnel",
            columns=(
                FormCollectionColumnDefinition(
                    name="role",
                    field_name="role",
                ),
            ),
            allow_delete=False,
        )

        collection = ResolvedFormCollection(
            definition=definition,
            formset=formset,
        )

        self.assertFalse(collection.allow_delete)
        self.assertTrue(collection.formset.can_delete)