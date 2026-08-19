

from __future__ import annotations

from decimal import Decimal

from django import forms
from django.forms import BaseModelFormSet, modelformset_factory

from apps.reporting.models import ActivityReportEntry


class ActivityReportEntryForm(forms.ModelForm):
    """
    Saisie journalière d'une ligne de rapport d'activité.
    """

    class Meta:
        model = ActivityReportEntry

        fields = (
            "regular_hours",
            "overtime_hours",
        )

        widgets = {
            "regular_hours": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.25",
                    "inputmode": "decimal",
                    "class": (
                        "w-16 rounded-md border "
                        "border-axcio-border-light "
                        "bg-axcio-surface px-2 py-1.5 "
                        "text-center text-sm "
                        "text-axcio-text "
                        "focus:border-axcio-light "
                        "focus:outline-none focus:ring-1 "
                        "focus:ring-axcio-light "
                        "dark:border-axcio-border-dark "
                        "dark:bg-axcio-surface-dark "
                        "dark:text-axcio-text-dark"
                    ),
                }
            ),
            "overtime_hours": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.25",
                    "inputmode": "decimal",
                    "class": (
                        "w-16 rounded-md border "
                        "border-axcio-border-light "
                        "bg-axcio-surface px-2 py-1.5 "
                        "text-center text-sm "
                        "text-axcio-text "
                        "focus:border-axcio-light "
                        "focus:outline-none focus:ring-1 "
                        "focus:ring-axcio-light "
                        "dark:border-axcio-border-dark "
                        "dark:bg-axcio-surface-dark "
                        "dark:text-axcio-text-dark"
                    ),
                }
            ),
        }

    def clean_regular_hours(self):
        value = (
            self.cleaned_data.get("regular_hours")
            or Decimal("0.00")
        )

        if value < 0:
            raise forms.ValidationError(
                "Le nombre d'heures ne peut pas être négatif."
            )

        return value

    def clean_overtime_hours(self):
        value = (
            self.cleaned_data.get("overtime_hours")
            or Decimal("0.00")
        )

        if value < 0:
            raise forms.ValidationError(
                "Le nombre d'heures ne peut pas être négatif."
            )

        return value


class BaseActivityReportEntryFormSet(
    BaseModelFormSet
):
    """
    Formset utilisé pour la saisie de toutes les cases horaires
    d'un rapport d'activité.
    """

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        seen_entries = set()

        for form in self.forms:
            instance = form.instance

            if instance.pk is None:
                continue

            if instance.pk in seen_entries:
                raise forms.ValidationError(
                    "Une saisie journalière est présente plusieurs fois."
                )

            seen_entries.add(instance.pk)


ActivityReportEntryFormSet = modelformset_factory(
    ActivityReportEntry,
    form=ActivityReportEntryForm,
    formset=BaseActivityReportEntryFormSet,
    extra=0,
)