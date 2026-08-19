

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.users.models import User
from apps.work.models import WorkPackage
from common.constants.task import (
    TASK_ASSIGNMENT_DEFAULT_ALLOCATION_PERCENT,
    TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT,
    TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT,
    TASK_CODE_LENGTH,
    TASK_DESCRIPTION_LENGTH,
    TASK_MAX_PROGRESS_PERCENT,
    TASK_MIN_PROGRESS_PERCENT,
    TASK_NAME_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField

from .models import (
    Task,
    TaskAssignment,
)


class TaskForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'une tâche.
    """

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="TASK_STATUS",
        required=True,
        label="Statut",
    )

    class Meta:
        model = Task

        fields = (
            "work_package",
            "status",
            "code",
            "name",
            "description",
            "initial_start_date",
            "initial_end_date",
            "start_date",
            "end_date",
            "planned_workload_hours",
            "remaining_workload_hours",
            "progress_percent",
            "is_active",
        )

        labels = {
            "initial_start_date": "Début initial",
            "initial_end_date": "Fin initiale",
            "start_date": "Début",
            "end_date": "Fin",
            "is_active": "Tâche active",
        }

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "maxlength": TASK_CODE_LENGTH,
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
                    "maxlength": TASK_NAME_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "Nom de la tâche",
                    "data-trim": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "maxlength": TASK_DESCRIPTION_LENGTH,
                    "rows": 4,
                    "placeholder": "Description de la tâche",
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
            "remaining_workload_hours": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
            "progress_percent": forms.NumberInput(
                attrs={
                    "min": TASK_MIN_PROGRESS_PERCENT,
                    "max": TASK_MAX_PROGRESS_PERCENT,
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["code"].required = False

        self.fields["work_package"].queryset = (
            WorkPackage.objects
            .filter(is_active=True)
            .select_related("project")
            .order_by(
                "project__reference",
                "code",
                "name",
            )
        )

        self._configure_catalog_field(
            field_name="status",
            catalog_code="TASK_STATUS",
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


class TaskAssignmentForm(forms.ModelForm):
    """
    Affectation individuelle d'un utilisateur à une tâche.
    """

    role = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="TASK_MEMBER_ROLE",
        required=True,
        label="Rôle sur la tâche",
    )

    class Meta:
        model = TaskAssignment

        fields = (
            "user",
            "role",
            "allocation_percent",
            "is_active",
        )

        labels = {
            "user": "Utilisateur",
            "allocation_percent": "Taux de charge (%)",
            "is_active": "Actif",
        }

        widgets = {
            "allocation_percent": forms.NumberInput(
                attrs={
                    "min": (
                        TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT
                    ),
                    "max": (
                        TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT
                    ),
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(
        self,
        *args,
        project=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fields["user"].queryset = (
            User.objects.none()
        )

        if project is not None:
            self.fields["user"].queryset = (
                User.objects
                .filter(
                    is_active=True,
                    project_memberships__project=project,
                    project_memberships__is_active=True,
                )
                .select_related(
                    "company",
                    "job",
                    "global_role",
                    "access_level",
                )
                .distinct()
                .order_by(
                    "last_name",
                    "first_name",
                )
            )

        self.fields["role"].queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code="TASK_MEMBER_ROLE",
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related("catalog_type")
            .order_by(
                "sort_order",
                "label",
            )
        )

        self.fields["role"].catalog_is_editable = False
        self.fields["role"].catalog_is_incremental = False

        if not self.is_bound and not self.instance.pk:
            default_value = (
                self.fields["role"]
                .queryset
                .filter(is_default=True)
                .first()
            )

            if default_value is not None:
                self.initial["role"] = default_value.pk

            self.initial["allocation_percent"] = (
                TASK_ASSIGNMENT_DEFAULT_ALLOCATION_PERCENT
            )


class BaseTaskAssignmentFormSet(
    forms.BaseInlineFormSet
):
    """
    Formset des personnes affectées à une tâche.
    """

    def __init__(
        self,
        *args,
        project=None,
        **kwargs,
    ) -> None:
        self.project = project

        super().__init__(
            *args,
            **kwargs,
        )

    def get_form_kwargs(
        self,
        index,
    ):
        kwargs = super().get_form_kwargs(index)

        kwargs["project"] = self.project

        return kwargs


TaskAssignmentFormSet = forms.inlineformset_factory(
    Task,
    TaskAssignment,
    form=TaskAssignmentForm,
    formset=BaseTaskAssignmentFormSet,
    fields=(
        "user",
        "role",
        "allocation_percent",
        "is_active",
    ),
    extra=0,
    can_delete=True,
)