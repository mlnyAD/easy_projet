

from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError

from apps.documents.models import Document
from common.constants.document import (
    DOCUMENT_IMPORT_MAX_FILES,
)
from common.forms.widgets import FileUploadInput


class MultipleFileInput(FileUploadInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(
        self,
        data,
        initial=None,
    ) -> list:
        if not data:
            return super().clean(
                data,
                initial,
            )

        if not isinstance(data, list):
            data = [data]

        if len(data) > DOCUMENT_IMPORT_MAX_FILES:
            raise ValidationError(
                (
                    "Vous pouvez importer au maximum "
                    f"{DOCUMENT_IMPORT_MAX_FILES} fichiers "
                    "à la fois."
                )
            )

        single_file_clean = super().clean

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
        max_length=Document._meta.get_field(
            "description"
        ).max_length,
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