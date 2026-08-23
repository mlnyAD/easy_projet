

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.documents.models import DocumentFolder
from common.forms.fields import CatalogModelChoiceField


class DocumentCreateForm(forms.Form):
    """
    Création d'un document documentaire natif.
    """

    FORMAT_WORD = "word"
    FORMAT_EXCEL = "excel"
    FORMAT_POWERPOINT = "powerpoint"

    FORMAT_CHOICES = (
        (
            FORMAT_WORD,
            "Document Word",
        ),
        (
            FORMAT_EXCEL,
            "Classeur Excel",
        ),
        (
            FORMAT_POWERPOINT,
            "Présentation PowerPoint",
        ),
    )

    title = forms.CharField(
        label="Titre",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "data-trim": True,
            }
        ),
    )

    document_format = forms.ChoiceField(
        label="Format",
        choices=FORMAT_CHOICES,
    )

    folder = forms.ModelChoiceField(
        label="Dossier",
        queryset=DocumentFolder.objects.none(),
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
        project,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.project = project

        self.fields["folder"].queryset = (
            DocumentFolder.objects
            .filter(
                project=project,
                is_active=True,
            )
            .order_by(
                "sort_order",
                "name",
            )
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