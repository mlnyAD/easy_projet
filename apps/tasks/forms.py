

"""
Formulaires du domaine des tâches.
"""

from __future__ import annotations

from decimal import Decimal

from django import forms
from django.db.models import Q

from apps.catalogs.models import CatalogValue
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
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
    TaskDependency,
)
from .services import TaskWorkloadService

TASK_DATE_FORMAT = "%Y-%m-%d"

TASK_DATE_FIELD_NAMES = (
    "initial_start_date",
    "initial_end_date",
    "start_date",
    "end_date",
)


def task_date_input() -> forms.DateInput:
    return forms.DateInput(
        format=TASK_DATE_FORMAT,
        attrs={
            "type": "date",
        },
    )

class TaskForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'une tâche.
    """

    consumed_workload_hours = forms.DecimalField(
        required=False,
        disabled=True,
        decimal_places=2,
        label="Consommé (h)",
        widget=forms.NumberInput(
            attrs={
                "step": "0.25",
                "class": "ep-input",
            }
        ),
    )

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
            "initial_start_date": task_date_input(),
            "initial_end_date": task_date_input(),
            "start_date": task_date_input(),
            "end_date": task_date_input(),
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
                    "step": "0.25",
                    "inputmode": "decimal",
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

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        
        for field_name in TASK_DATE_FIELD_NAMES:
            self.fields[field_name].input_formats = [
                TASK_DATE_FORMAT,
            ]

        self.fields["code"].required = False

        self.fields["consumed_workload_hours"].help_text = (
            "Calculé à partir des rapports d'activité validés."
        )

        if self.instance.remaining_workload_hours_is_manual:
            self.fields["remaining_workload_hours"].help_text = (
                "Valeur corrigée manuellement."
            )
        else:
            self.fields["remaining_workload_hours"].help_text = (
                "Calculé automatiquement à partir du consommé."
            )

        if self.instance.progress_percent_is_manual:
            self.fields["progress_percent"].help_text = (
                "Valeur corrigée manuellement."
            )
        else:
            self.fields["progress_percent"].help_text = (
                "Calculé automatiquement à partir du consommé."
            )

        if self.instance.pk:
            consumed_hours = (
                TaskWorkloadService
                .get_consumed_hours_by_task(
                    task_ids=(self.instance.pk,)
                )
                .get(
                    self.instance.pk,
                    Decimal("0.00"),
                )
            )

            self.initial["consumed_workload_hours"] = (
                consumed_hours
            )

        if user is None:
            self.fields["work_package"].queryset = (
                self.fields["work_package"]
                .queryset
                .none()
            )
        else:
            workable_projects = (
                ProjectAuthorizationService
                .get_workable_projects(user)
            )

            work_package_filter = Q(
                project__in=workable_projects,
                is_active=True,
            )

            if self.instance.pk:
                work_package_filter |= Q(
                    pk=self.instance.work_package_id,
                )

            self.fields["work_package"].queryset = (
                WorkPackage.objects
                .filter(
                    work_package_filter,
                )
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

        if (
            not self.is_bound
            and self.instance._state.adding
        ):
            self._apply_catalog_default("status")

    def clean(self):
        cleaned_data = super().clean()

        planned_hours = cleaned_data.get(
            "planned_workload_hours"
        )

        if planned_hours is None:
            return cleaned_data

        if self.instance._state.adding:
            if (
                "remaining_workload_hours"
                not in self.changed_data
            ):
                cleaned_data[
                    "remaining_workload_hours"
                ] = Decimal(planned_hours)
            else:
                self.instance.remaining_workload_hours_is_manual = (
                    True
                )

            if "progress_percent" in self.changed_data:
                self.instance.progress_percent_is_manual = True

            return cleaned_data

        if "remaining_workload_hours" in self.changed_data:
            self.instance.remaining_workload_hours_is_manual = True

        if "progress_percent" in self.changed_data:
            self.instance.progress_percent_is_manual = True

        return cleaned_data

    def save(
        self,
        commit=True,
    ) -> Task:
        task = super().save(commit=commit)

        if commit:
            TaskWorkloadService.synchronize_tasks(
                task_ids=(task.pk,)
            )

        return task

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

        if default_value is None:
            return

        self.fields[field_name].initial = (
            default_value.pk
        )

        self.initial[field_name] = (
            default_value.pk
        )

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

        if not self.is_bound and self.instance._state.adding:
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


class TaskDependencyForm(forms.ModelForm):
    """
    Dépendance d'ordonnancement vers la tâche courante.

    La tâche courante est la successeure.
    L'utilisateur choisit uniquement l'antécédent.
    """

    class Meta:
        model = TaskDependency

        fields = (
            "predecessor",
            "dependency_type",
            "lag_days",
            "is_active",
        )

        labels = {
            "predecessor": "Tâche antécédente",
            "dependency_type": "Type",
            "lag_days": "Décalage (jours)",
            "is_active": "Actif",
        }

        widgets = {
            "lag_days": forms.NumberInput(
                attrs={
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(
        self,
        *args,
        task=None,
        project=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.task = task
        self.project = project

        queryset = (
            Task.objects
            .filter(
                is_active=True,
            )
            .select_related(
                "work_package",
                "work_package__project",
            )
            .order_by(
                "work_package__code",
                "code",
                "name",
            )
        )

        if project is not None:
            queryset = queryset.filter(
                work_package__project=project,
            )

        if task is not None and task.pk:
            queryset = queryset.exclude(
                pk=task.pk,
            )

        self.fields["predecessor"].queryset = queryset

        if (
            not self.is_bound
            and self.instance._state.adding
        ):
            self.initial["dependency_type"] = (
                TaskDependency
                .DependencyType
                .FINISH_TO_START
            )

            self.initial["lag_days"] = 0


class BaseTaskDependencyFormSet(
    forms.BaseInlineFormSet
):
    """
    Formset des antécédents d'une tâche.

    La tâche courante est toujours la successeure.
    """

    def __init__(
        self,
        *args,
        task=None,
        project=None,
        **kwargs,
    ) -> None:
        self.task = task
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

        kwargs["task"] = self.task
        kwargs["project"] = self.project

        return kwargs


TaskDependencyFormSet = forms.inlineformset_factory(
    Task,
    TaskDependency,
    fk_name="successor",
    form=TaskDependencyForm,
    formset=BaseTaskDependencyFormSet,
    fields=(
        "predecessor",
        "dependency_type",
        "lag_days",
        "is_active",
    ),
    extra=0,
    can_delete=True,
)
