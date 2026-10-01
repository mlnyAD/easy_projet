from urllib.parse import urlencode
from uuid import UUID


from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin

from django.shortcuts import get_object_or_404

from django.urls import reverse

from django.utils.http import url_has_allowed_host_and_scheme

from django.views.generic import ListView


from apps.projects.models import Project

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)

from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)

from framework.runtime import EPList, ListPage

from framework.integrations.django.viewmodel import (
    DjangoListViewModelBuilder,
)


from .form_definition import RISK_FORM_DEFINITION

from .forms import RiskForm

from .lists import RISK_LIST_DEFINITION

from .models import Risk

from apps.projects.services.access import (
    ProjectAccessService,
)

from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
from apps.catalogs.models import CatalogValue
from apps.users.models import User

from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)


class RiskListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    """
    Liste globale des risques et opportunités.
    """

    model = Risk
    template_name = "risks/risk_list.html"
    context_object_name = "risks"

    list_definition = RISK_LIST_DEFINITION

    project_parameter = "project"
    risk_type_parameter = "risk_type"
    owner_parameter = "owner"
    criticality_parameter = "criticality"
    status_parameter = "status"
    activity_parameter = "activity"

    activity_all = "all"
    activity_active = "active"
    activity_inactive = "inactive"

    activity_values = (
        activity_all,
        activity_active,
        activity_inactive,
    )

    def get_sort_field_map(self) -> dict[str, str]:
        sort_field_map = super().get_sort_field_map()

        sort_field_map.update(
            {
                "project": "project__reference",
                "risk_type": "risk_type__sort_order",
                "owner": "owner__last_name",
                "criticality": "criticality__sort_order",
                "probability": "probability__sort_order",
                "status": "status__sort_order",
            }
        )

        return sort_field_map

    def get_accessible_projects(self):
        return ProjectAccessService.get_accessible_projects(self.request.user)

    def get_risk_scope(self):
        return Risk.objects.filter(
            project__in=self.get_accessible_projects(),
        ).select_related(
            "project",
            "owner",
            "origin",
            "risk_type",
            "risk_class",
            "impact",
            "severity",
            "probability",
            "status",
            "criticality",
            "review_frequency",
        )

    def get_filter_projects(self):
        return self.get_accessible_projects().order_by(
            "reference",
            "name",
        )

    def get_filter_risk_types(self):
        risk_type_ids = self.get_risk_scope().values_list(
            "risk_type_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=risk_type_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_filter_owners(self):
        owner_ids = (
            self.get_risk_scope()
            .exclude(owner__isnull=True)
            .values_list("owner_id", flat=True)
        )

        return User.objects.filter(
            pk__in=owner_ids,
        ).order_by(
            "last_name",
            "first_name",
        )

    def get_filter_criticalities(self):
        criticality_ids = self.get_risk_scope().values_list(
            "criticality_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=criticality_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_filter_statuses(self):
        status_ids = self.get_risk_scope().values_list(
            "status_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=status_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_project_filter(self) -> str | None:
        raw_project_id = self.request.GET.get(
            self.project_parameter,
            "",
        ).strip()

        if not raw_project_id:
            return None

        try:
            project_id = UUID(raw_project_id)
        except ValueError:
            return None

        if (
            not self.get_filter_projects()
            .filter(
                pk=project_id,
            )
            .exists()
        ):
            return None

        return str(project_id)

    def get_catalog_filter(
        self,
        *,
        parameter: str,
        queryset,
    ) -> int | None:
        raw_value = self.request.GET.get(
            parameter,
            "",
        ).strip()

        if not raw_value:
            return None

        try:
            value_id = int(raw_value)
        except ValueError:
            return None

        if not queryset.filter(pk=value_id).exists():
            return None

        return value_id

    def get_risk_type_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.risk_type_parameter,
            queryset=self.get_filter_risk_types(),
        )

    def get_owner_filter(self) -> str | None:
        raw_owner_id = self.request.GET.get(
            self.owner_parameter,
            "",
        ).strip()

        if not raw_owner_id:
            return None

        try:
            owner_id = UUID(raw_owner_id)
        except ValueError:
            return None

        if (
            not self.get_filter_owners()
            .filter(
                pk=owner_id,
            )
            .exists()
        ):
            return None

        return str(owner_id)

    def get_criticality_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.criticality_parameter,
            queryset=self.get_filter_criticalities(),
        )

    def get_status_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.status_parameter,
            queryset=self.get_filter_statuses(),
        )

    def get_activity_filter(self) -> str:
        activity = self.request.GET.get(
            self.activity_parameter,
            self.activity_active,
        )

        if activity not in self.activity_values:
            return self.activity_active

        return activity

    def get_queryset(self):
        queryset = self.get_risk_scope()

        project_id = self.get_project_filter()
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        risk_type_id = self.get_risk_type_filter()
        if risk_type_id is not None:
            queryset = queryset.filter(risk_type_id=risk_type_id)

        owner_id = self.get_owner_filter()
        if owner_id is not None:
            queryset = queryset.filter(owner_id=owner_id)

        criticality_id = self.get_criticality_filter()
        if criticality_id is not None:
            queryset = queryset.filter(criticality_id=criticality_id)

        status_id = self.get_status_filter()
        if status_id is not None:
            queryset = queryset.filter(status_id=status_id)

        activity = self.get_activity_filter()
        if activity != self.activity_all:
            queryset = queryset.filter(
                is_active=activity == self.activity_active,
            )

        return queryset

    def get_return_url(self) -> str:
        return self.request.get_full_path()

    def get_create_project(self) -> Project | None:
        return None

    def get_create_url(self) -> str:
        parameters = {
            "next": self.get_return_url(),
        }

        project = self.get_create_project()
        if project is not None:
            parameters["project"] = str(project.pk)

        return f"{reverse('risks:create')}?{urlencode(parameters)}"

    def get_page_title(self) -> str:
        return "Risques"

    def get_page_subtitle(self) -> str:
        return ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=self.list_definition,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(django_page.object_list),
            page=django_page.number,
            page_size=django_page.paginator.per_page,
            total_items=django_page.paginator.count,
            total_pages=django_page.paginator.num_pages,
            has_previous=django_page.has_previous(),
            has_next=django_page.has_next(),
        )

        visible_column_identifiers = self.get_visible_column_identifiers()
        sort_by = self.get_sort_by()
        sort_descending = self.get_sort_descending()

        context["list_view"] = DjangoListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(visible_column_identifiers),
        )
        context["list"] = context["list_view"]

        context["list_definition"] = self.get_list_definition()
        context["visible_column_identifiers"] = visible_column_identifiers
        context["can_save_list_preferences"] = self.request.user.is_authenticated

        context["sort_by"] = sort_by
        context["sort_descending"] = sort_descending

        context["filter_projects"] = self.get_filter_projects()
        context["filter_risk_types"] = self.get_filter_risk_types()
        context["filter_owners"] = self.get_filter_owners()
        context["filter_criticalities"] = self.get_filter_criticalities()
        context["filter_statuses"] = self.get_filter_statuses()

        context["project_filter"] = self.get_project_filter()
        context["risk_type_filter"] = self.get_risk_type_filter()
        context["owner_filter"] = self.get_owner_filter()
        context["criticality_filter"] = self.get_criticality_filter()
        context["status_filter"] = self.get_status_filter()
        context["risk_activity"] = self.get_activity_filter()

        context["list_filters_template"] = "risks/risk_list_filters.html"
        context["row_actions_template"] = "risks/risk_actions.html"
        context["is_project_context"] = False
        context["return_url"] = self.get_return_url()

        can_create_risk = ProjectAuthorizationService.get_workable_projects(
            self.request.user
        ).exists()

        context["page_action_url"] = self.get_create_url() if can_create_risk else None
        context["page_title"] = self.get_page_title()
        context["page_subtitle"] = self.get_page_subtitle()

        return context


class RiskListByProjectView(RiskListView):
    """

    Liste des risques et opportunités d'un projet donné.

    """

    def get_project(self) -> Project:

        if not hasattr(
            self,
            "_project",
        ):
            self._project = get_object_or_404(
                ProjectAccessService.get_accessible_projects(
                    self.request.user
                ).select_related(
                    "owner_company",
                    "status",
                ),
                pk=self.kwargs["project_pk"],
            )

        return self._project

    def get_risk_scope(self):
        return (
            super()
            .get_risk_scope()
            .filter(
                project=self.get_project(),
            )
        )

    def get_queryset(self):
        return super().get_queryset()

    def get_return_url(self) -> str:
        return self.request.get_full_path()

    # ------------------------------------------------------------------

    # Navigation

    # ------------------------------------------------------------------

    def get_return_url(self) -> str:
        """

        Depuis le contexte projet, la création ou modification

        revient au résumé du projet.

        """

        project = self.get_project()

        return reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

    def get_create_project(self) -> Project:
        """

        Présélectionne le projet courant lors de la création.

        """

        return self.get_project()

    # ------------------------------------------------------------------

    # Présentation

    # ------------------------------------------------------------------

    def get_page_title(self) -> str:

        return "Risques du projet"

    def get_page_subtitle(self) -> str:

        project = self.get_project()

        return f"{project.reference} — {project.name}"

    # ------------------------------------------------------------------

    # Contexte

    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project

        context["current_project"] = project

        context["is_project_context"] = True

        if not (
            ProjectAuthorizationService.can_work_on_project(
                user=self.request.user,
                project=project,
            )
        ):
            context["page_action_url"] = None

        return context


class RiskCreateView(
    UserPassesTestMixin,
    EPCreateView,
):
    model = Risk

    form_class = RiskForm

    definition = RISK_FORM_DEFINITION

    template_name = "edf/form/view.html"

    def test_func(self):

        return ProjectAuthorizationService.get_workable_projects(
            self.request.user
        ).exists()

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_return_url(self):

        candidate = self.request.GET.get("next")

        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=(self.request.is_secure()),
        ):
            return candidate

        return reverse("risks:list")

    def get_success_url(self):

        return self.get_return_url()

    def get_cancel_url(self):

        return self.get_return_url()

    def get_initial(self):

        initial = super().get_initial()

        project_pk = self.request.GET.get("project")

        if project_pk:
            project = (
                ProjectAuthorizationService.get_workable_projects(self.request.user)
                .filter(
                    pk=project_pk,
                    is_active=True,
                )
                .first()
            )

            if project is not None:
                initial["project"] = project

        return initial

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le risque a été créé avec succès.",
        )

        return response


class RiskUpdateView(EPUpdateView):
    model = Risk

    form_class = RiskForm

    definition = RISK_FORM_DEFINITION

    template_name = "edf/form/view.html"

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_queryset(self):

        accessible_projects = ProjectAccessService.get_accessible_projects(
            self.request.user
        )

        return Risk.objects.filter(
            project__in=accessible_projects,
        ).select_related(
            "project",
            "owner",
            "origin",
            "risk_type",
            "risk_class",
            "impact",
            "severity",
            "probability",
            "status",
            "criticality",
            "review_frequency",
        )

    def can_edit_object(self) -> bool:
        """

        Indique si l'utilisateur peut modifier le risque courant.

        """

        return ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=self.object.project,
        )

    def get_return_url(self):

        candidate = self.request.GET.get("next")

        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=(self.request.is_secure()),
        ):
            return candidate

        return reverse("risks:list")

    def get_success_url(self):

        return self.get_return_url()

    def get_cancel_url(self):

        return self.get_return_url()

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le risque a été modifié avec succès.",
        )

        return response
