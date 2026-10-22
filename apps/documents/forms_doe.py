

from __future__ import annotations

from django import forms

from apps.client_configuration.models import DoeTemplate
from apps.projects.models import Project


class DoeGenerateForm(forms.Form):
    """
    Choix facultatif du modèle utilisé pour générer un DOE.
    """

    doe_template = forms.ModelChoiceField(
        label="Modèle de DOE",
        queryset=DoeTemplate.objects.none(),
        required=False,
        empty_label=(
            "Sans modèle — reproduire "
            "l'arborescence source"
        ),
        widget=forms.Select(
            attrs={
                "class": (
                    "mt-1 block w-full rounded-md border "
                    "border-axcio-border-light "
                    "bg-axcio-surface px-3 py-2 text-sm "
                    "shadow-sm outline-none "
                    "focus:border-axcio-light "
                    "focus:ring-1 focus:ring-axcio-light "
                    "dark:border-axcio-border-dark "
                    "dark:bg-axcio-surface-dark"
                ),
            },
        ),
    )

    def __init__(
        self,
        *args,
        project: Project,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        queryset = (
            DoeTemplate.objects
            .filter(
                client_environment=(
                    project.client_environment
                ),
                is_active=True,
                folders__is_active=True,
            )
            .distinct()
            .order_by("name")
        )

        self.fields["doe_template"].queryset = queryset
        self.has_available_templates = queryset.exists()