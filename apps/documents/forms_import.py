

from __future__ import annotations

from pathlib import Path

from django import forms

from apps.catalogs.models import CatalogValue
from common.forms.fields import CatalogModelChoiceField


class DocumentImportForm(forms.Form):
    """
    Import d'un document PDF dans la GED.
    """

    file = forms.FileField(
        label="Fichier PDF",
        required=True,
    )

    title = forms.CharField(
        label="Titre",
        max_length=255,
        required=False,
        help_text=(
            "Si vide, le nom du fichier sera utilisé."
        ),
    )

    document_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="DOCUMENT_TYPE",
        label="Type de document",
        required=True,
    )

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="DOCUMENT_STATUS",
        label="Statut",
        required=True,
    )

    lifecycle = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="DOCUMENT_LIFECYCLE",
        label="État GED",
        required=True,
    )

    is_doe = forms.BooleanField(
        label="Intégrer au DOE",
        required=False,
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self._configure_catalog_field(
            "document_type",
            "DOCUMENT_TYPE",
        )

        self._configure_catalog_field(
            "status",
            "DOCUMENT_STATUS",
        )

        self._configure_catalog_field(
            "lifecycle",
            "DOCUMENT_LIFECYCLE",
        )

        if not self.is_bound:
            self._apply_default(
                "status"
            )

            self._apply_default(
                "lifecycle"
            )

    def clean_file(self):
        uploaded_file = self.cleaned_data[
            "file"
        ]

        filename = uploaded_file.name

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        if extension != ".pdf":
            raise forms.ValidationError(
                "Seuls les fichiers PDF sont acceptés."
            )

        content_type = (
            getattr(
                uploaded_file,
                "content_type",
                "",
            )
            or ""
        )

        if (
            content_type
            and content_type
            != "application/pdf"
        ):
            raise forms.ValidationError(
                "Le fichier sélectionné n'est pas un PDF valide."
            )

        return uploaded_file

    def clean_title(self):
        title = (
            self.cleaned_data
            .get("title", "")
            .strip()
        )

        if title:
            return title

        uploaded_file = (
            self.cleaned_data
            .get("file")
        )

        if uploaded_file is None:
            return ""

        return Path(
            uploaded_file.name
        ).stem

    def _configure_catalog_field(
        self,
        field_name: str,
        catalog_code: str,
    ) -> None:
        field = self.fields[
            field_name
        ]

        field.queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related(
                "catalog_type"
            )
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

    def _apply_default(
        self,
        field_name: str,
    ) -> None:
        field = self.fields[
            field_name
        ]

        default_value = (
            field.queryset
            .filter(
                is_default=True
            )
            .first()
        )

        if default_value is not None:
            self.initial[
                field_name
            ] = default_value.pk