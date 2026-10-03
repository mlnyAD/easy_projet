

from __future__ import annotations

from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(
        self,
        data,
        initial=None,
    ) -> list:
        single_file_clean = super().clean

        if not isinstance(data, list):
            data = [data]

        return [
            single_file_clean(
                uploaded_file,
                initial,
            )
            for uploaded_file in data
        ]


class DocumentImportForm(forms.Form):
    """
    Import d'un ou plusieurs fichiers dans la GED.
    """

    files = MultipleFileField(
        label="Fichiers",
        required=True,
    )

    description = forms.CharField(
        label="Commentaire",
        max_length=1000,
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Ex. Visite du 3 octobre — avancement "
                    "des façades."
                ),
            }
        ),
        help_text=(
            "Ce commentaire sera appliqué à chaque document "
            "importé."
        ),
    )

    is_doe = forms.BooleanField(
        label="Intégrer au DOE",
        required=False,
    )