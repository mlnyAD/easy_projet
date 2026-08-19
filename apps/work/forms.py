

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.work_package import (
    WORK_PACKAGE_CODE_LENGTH,
    WORK_PACKAGE_DESCRIPTION_LENGTH,
    WORK_PACKAGE_NAME_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField

from .models import WorkPackage


class WorkPackageForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'un lot de travaux.
    """

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="WORK_PACKAGE_STATUS",
        required=True,
        label="Statut",
    )

    class Meta:
        model = WorkPackage

        fields = (
            "project",
            "code",
            "name",
            "description",
            "status",
            "manager",
            "initial_start_date",
            "initial_end_date",
            "start_date",
            "end_date",
            "planned_workload_hours",
            "is_active",
        )

        labels = {
            "initial_start_date": "Début initial",
            "initial_end_date": "Fin initiale",
            "start_date": "Début",
            "end_date": "Fin",
            "is_active": "Lot actif",
        }

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "maxlength": WORK_PACKAGE_CODE_LENGTH,
                    "autocomplete": "off",
                    "placeholder": (
                        "Généré automatiquement si vide"
                    ),
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "maxlength": WORK_PACKAGE_NAME_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "Nom du lot de travaux",
                    "data-trim": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "maxlength": WORK_PACKAGE_DESCRIPTION_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Description générale du lot de travaux"
                    ),
                    "data-trim": True,
                }
            ),
            "initial_start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "initial_end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "planned_workload_hours": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["code"].required = False

        self.fields["project"].queryset = (
            Project.objects
            .filter(is_active=True)
            .select_related("owner_company")
            .order_by(
                "reference",
                "name",
            )
        )

        self.fields["manager"].queryset = (
            User.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self._configure_catalog_field(
            field_name="status",
            catalog_code="WORK_PACKAGE_STATUS",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default("status")

    def _configure_catalog_field(
        self,
        *,
        field_name: str,
        catalog_code: str,
    ) -> None:
        catalog = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
            )
            .values(
                "catalog_type__is_editable",
                "catalog_type__is_incremental",
            )
            .first()
        )

        field = self.fields[field_name]

        field.queryset = (
            CatalogValue.objects
            .filter(
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

        if catalog is None:
            field.catalog_is_editable = False
            field.catalog_is_incremental = False
            return

        field.catalog_is_editable = (
            catalog["catalog_type__is_editable"]
        )
        field.catalog_is_incremental = (
            catalog["catalog_type__is_incremental"]
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(is_default=True)
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = default_value.pk