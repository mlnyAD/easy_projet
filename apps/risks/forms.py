

from __future__ import annotations

from django import forms
from django.db.models import Q

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
from apps.users.models import User
from common.constants.risk import (
    RISK_DESCRIPTION_LENGTH,
    RISK_PLANNED_ACTIONS_LENGTH,
    RISK_REFERENCE_LENGTH,
    RISK_TITLE_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField

from .models import Risk


class RiskForm(forms.ModelForm):
    """Formulaire de création et de modification d'un risque."""

    origin = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_ORIGIN", required=True, label="Origine")
    risk_type = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_TYPE", required=True, label="Type")
    risk_class = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_CLASS", required=True, label="Classe")
    impact = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_IMPACT", required=True, label="Impact")
    severity = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_GRAVITY", required=True, label="Gravité")
    probability = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_PROBABILITY", required=True, label="Probabilité")
    status = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_STATE", required=True, label="État")
    criticality = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_CRITICALITY", required=True, label="Criticité")
    review_frequency = CatalogModelChoiceField(queryset=CatalogValue.objects.none(), catalog_code="RISK_REVIEW_FREQUENCY", required=False, label="Fréquence de revue")

    class Meta:
        model = Risk
        fields = (
            "project", "owner", "origin", "risk_type", "risk_class",
            "impact", "severity", "probability", "status", "criticality",
            "review_frequency", "reference", "title", "description",
            "occurrence_date", "closure_date", "estimated_cost",
            "last_review_date", "planned_actions", "is_active",
        )
        labels = {"owner": "Pilote du risque", "is_active": "Risque actif"}
        widgets = {
            "reference": forms.TextInput(attrs={"maxlength": RISK_REFERENCE_LENGTH, "autocomplete": "off", "placeholder": "Générée automatiquement si vide", "data-uppercase": True, "data-trim": True}),
            "title": forms.TextInput(attrs={"maxlength": RISK_TITLE_LENGTH, "autocomplete": "off", "placeholder": "Titre du risque ou de l'opportunité", "data-trim": True}),
            "description": forms.Textarea(attrs={"maxlength": RISK_DESCRIPTION_LENGTH, "rows": 4, "placeholder": "Description du risque, de ses causes et de ses conséquences", "data-trim": True}),
            "occurrence_date": forms.DateInput(attrs={"type": "date"}),
            "closure_date": forms.DateInput(attrs={"type": "date"}),
            "estimated_cost": forms.NumberInput(attrs={"min": 0, "step": "0.01", "inputmode": "decimal", "placeholder": "Montant estimé"}),
            "last_review_date": forms.DateInput(attrs={"type": "date"}),
            "planned_actions": forms.Textarea(attrs={"maxlength": RISK_PLANNED_ACTIONS_LENGTH, "rows": 4, "placeholder": "Actions de prévention, de réduction, de transfert ou d'exploitation prévues", "data-trim": True}),
        }

    def __init__(self, *args, user=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["reference"].required = False

        if user is None:
            self.fields["project"].queryset = self.fields["project"].queryset.none()
        else:
            workable_projects = ProjectAuthorizationService.get_workable_projects(user)
            project_filter = Q(pk__in=workable_projects)
            if self.instance.pk:
                project_filter |= Q(pk=self.instance.project_id)
            self.fields["project"].queryset = (
                Project.objects.filter(project_filter)
                .select_related("owner_company")
                .order_by("reference", "name")
            )

        self.fields["owner"].queryset = (
            User.objects.filter(is_active=True)
            .select_related("company")
            .order_by("last_name", "first_name")
        )

        catalog_fields = (
            ("origin", "RISK_ORIGIN"), ("risk_type", "RISK_TYPE"),
            ("risk_class", "RISK_CLASS"), ("impact", "RISK_IMPACT"),
            ("severity", "RISK_GRAVITY"), ("probability", "RISK_PROBABILITY"),
            ("status", "RISK_STATE"), ("criticality", "RISK_CRITICALITY"),
            ("review_frequency", "RISK_REVIEW_FREQUENCY"),
        )
        for field_name, catalog_code in catalog_fields:
            self._configure_catalog_field(field_name=field_name, catalog_code=catalog_code)
        if not self.is_bound and self.instance._state.adding:
            for field_name, _ in catalog_fields:
                self._apply_catalog_default(field_name)

    def _configure_catalog_field(self, *, field_name: str, catalog_code: str) -> None:
        catalog = (
            CatalogValue.objects.filter(catalog_type__code=catalog_code, catalog_type__is_active=True)
            .values("catalog_type__is_editable", "catalog_type__is_incremental")
            .first()
        )
        field = self.fields[field_name]
        field.queryset = (
            CatalogValue.objects.filter(catalog_type__code=catalog_code, catalog_type__is_active=True, is_active=True)
            .select_related("catalog_type")
            .order_by("level", "sort_order", "label")
        )
        if catalog is None:
            field.catalog_is_editable = False
            field.catalog_is_incremental = False
            return
        field.catalog_is_editable = catalog["catalog_type__is_editable"]
        field.catalog_is_incremental = catalog["catalog_type__is_incremental"]

    def _apply_catalog_default(self, field_name: str) -> None:
        default_value = self.fields[field_name].queryset.filter(is_default=True).first()
        if default_value is not None:
            self.initial[field_name] = default_value.pk
