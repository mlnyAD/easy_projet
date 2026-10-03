

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.documents.models import DocumentFolder
from common.forms.fields import CatalogModelChoiceField
from apps.documents.models import (
    Document,
    DocumentFolder,
)


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
            

class DocumentPropertiesForm(forms.ModelForm):
    """
    Propriétés métier et techniques d'un document.

    Les données techniques sont renseignées automatiquement
    à partir de la version courante et ne sont pas modifiables.
    """

    folder_path = forms.CharField(
        label="Dossier",
        required=False,
        disabled=True,
    )

    original_filename = forms.CharField(
        label="Fichier",
        required=False,
        disabled=True,
    )

    technical_type = forms.CharField(
        label="Format détecté",
        required=False,
        disabled=True,
    )

    version_number = forms.CharField(
        label="Version",
        required=False,
        disabled=True,
    )

    document_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="DOCUMENT_TYPE",
        label="Type de document",
        required=False,
    )

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="DOCUMENT_STATUS",
        label="Statut",
        required=False,
    )

    class Meta:
        model = Document

        fields = (
            "title",
            "description",
            "document_type",
            "status",
            "is_doe",
        )

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Ajouter un commentaire au document"
                    ),
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
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

        self._set_technical_values()

    def _configure_catalog_field(
        self,
        field_name: str,
        catalog_code: str,
    ) -> None:
        field = self.fields[field_name]

        field.queryset = (
            CatalogValue.objects.filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related("catalog_type")
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

        field.empty_label = "Non renseigné"

    def _set_technical_values(self) -> None:
        self.fields["folder_path"].initial = (
            self.instance.folder.full_path
        )

        version = self.instance.current_version

        if version is None:
            self.fields["original_filename"].initial = "—"
            self.fields["technical_type"].initial = "—"
            self.fields["version_number"].initial = "—"
            return

        self.fields["original_filename"].initial = (
            version.original_filename
        )

        self.fields["technical_type"].initial = (
            version.get_technical_type_display()
        )

        self.fields["version_number"].initial = (
            f"V{version.version_number}"
        )