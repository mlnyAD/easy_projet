from urllib.parse import urlencode
from uuid import UUID
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from apps.catalogs.models import CatalogValue
from apps.core.models import ClientEnvironment

from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import (
    EXTERNAL_INTEGRATION_FORM_DEFINITION,
)
from .forms import ExternalIntegrationForm
from .lists import EXTERNAL_INTEGRATION_LIST_DEFINITION
from .models import ExternalIntegration
from .services.access import IntegrationAccessService


def get_allowed_return_url(
    request,
    *,
    default_url,
):
    """
    Retourne l'URL de retour demandée si elle est sûre.
    """
    candidate = request.GET.get("next")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return default_url


class ExternalIntegrationListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    """
    Liste des intégrations externes accessibles.
    """

    model = ExternalIntegration
    template_name = "integrations/integration_list.html"
    context_object_name = "integrations"

    list_definition = EXTERNAL_INTEGRATION_LIST_DEFINITION

    client_environment_parameter = "client_environment"
    service_type_parameter = "service_type"
    provider_parameter = "provider"
    connection_status_parameter = "connection_status"
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
                "client_environment": ("client_environment__company__name"),
                "service_type": "service_type__sort_order",
                "provider": "provider__sort_order",
                "connection_status": ("connection_status__sort_order"),
            }
        )

        return sort_field_map

    def get_integration_scope(self):
        return IntegrationAccessService.get_accessible_integrations(self.request.user)

    def get_filter_client_environments(self):
        environment_ids = self.get_integration_scope().values_list(
            "client_environment_id",
            flat=True,
        )

        return (
            ClientEnvironment.objects.filter(pk__in=environment_ids)
            .select_related("company")
            .order_by("company__name")
        )

    def get_filter_catalog_values(self, field_name: str):
        value_ids = self.get_integration_scope().values_list(
            f"{field_name}_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=value_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_filter_service_types(self):
        return self.get_filter_catalog_values("service_type")

    def get_filter_providers(self):
        return self.get_filter_catalog_values("provider")

    def get_filter_connection_statuses(self):
        return self.get_filter_catalog_values("connection_status")

    def get_client_environment_filter(self) -> str | None:
        raw_environment_id = self.request.GET.get(
            self.client_environment_parameter,
            "",
        ).strip()

        if not raw_environment_id:
            return None

        try:
            environment_id = UUID(raw_environment_id)
        except ValueError:
            return None

        if (
            not self.get_filter_client_environments()
            .filter(
                pk=environment_id,
            )
            .exists()
        ):
            return None

        return str(environment_id)

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

    def get_service_type_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.service_type_parameter,
            queryset=self.get_filter_service_types(),
        )

    def get_provider_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.provider_parameter,
            queryset=self.get_filter_providers(),
        )

    def get_connection_status_filter(self) -> int | None:
        return self.get_catalog_filter(
            parameter=self.connection_status_parameter,
            queryset=self.get_filter_connection_statuses(),
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
        queryset = (
            super()
            .get_queryset()
            .filter(pk__in=self.get_integration_scope())
            .select_related(
                "client_environment",
                "client_environment__company",
                "service_type",
                "provider",
                "connection_status",
            )
        )

        client_environment_id = self.get_client_environment_filter()
        if client_environment_id is not None:
            queryset = queryset.filter(
                client_environment_id=client_environment_id,
            )

        service_type_id = self.get_service_type_filter()
        if service_type_id is not None:
            queryset = queryset.filter(
                service_type_id=service_type_id,
            )

        provider_id = self.get_provider_filter()
        if provider_id is not None:
            queryset = queryset.filter(
                provider_id=provider_id,
            )

        connection_status_id = self.get_connection_status_filter()
        if connection_status_id is not None:
            queryset = queryset.filter(
                connection_status_id=connection_status_id,
            )

        activity = self.get_activity_filter()
        if activity != self.activity_all:
            queryset = queryset.filter(
                is_active=activity == self.activity_active,
            )

        return queryset

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

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(visible_column_identifiers),
        )

        context["list_view"] = list_view
        context["list"] = list_view

        context["list_definition"] = self.get_list_definition()
        context["visible_column_identifiers"] = visible_column_identifiers
        context["can_save_list_preferences"] = self.request.user.is_authenticated

        context["sort_by"] = sort_by
        context["sort_descending"] = sort_descending

        context["filter_client_environments"] = self.get_filter_client_environments()
        context["filter_service_types"] = self.get_filter_service_types()
        context["filter_providers"] = self.get_filter_providers()
        context["filter_connection_statuses"] = self.get_filter_connection_statuses()

        context["client_environment_filter"] = self.get_client_environment_filter()
        context["service_type_filter"] = self.get_service_type_filter()
        context["provider_filter"] = self.get_provider_filter()
        context["connection_status_filter"] = self.get_connection_status_filter()
        context["integration_activity"] = self.get_activity_filter()

        context["list_filters_template"] = "integrations/integration_list_filters.html"
        context["row_actions_template"] = "integrations/integration_actions.html"
        context["return_url"] = self.request.get_full_path()

        context["page_title"] = "Intégrations externes"
        context["page_subtitle"] = (
            "Applications et services externes disponibles "
            "dans les environnements clients."
        )
        context["page_back_url"] = None
        context["page_back_label"] = None

        can_create = IntegrationAccessService.can_create_integration(self.request.user)

        context["page_action_label"] = "Nouvelle intégration" if can_create else None
        context["page_action_icon"] = "plus" if can_create else None
        context["page_action_url"] = (
            (
                f"{reverse('integrations:create')}?"
                f"{urlencode({'next': self.request.get_full_path()})}"
            )
            if can_create
            else None
        )

        return context


class ExternalIntegrationCreateView(EPCreateView):
    """
    Création d'une intégration externe.
    """

    model = ExternalIntegration
    form_class = ExternalIntegrationForm
    definition = EXTERNAL_INTEGRATION_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def dispatch(self, request, *args, **kwargs):
        if not IntegrationAccessService.can_create_integration(request.user):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse("integrations:list"),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "L'intégration externe a été créée avec succès.",
        )

        return response


class ExternalIntegrationUpdateView(EPUpdateView):
    """
    Modification d'une intégration externe.
    """

    model = ExternalIntegration
    form_class = ExternalIntegrationForm
    definition = EXTERNAL_INTEGRATION_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_queryset(self):
        return IntegrationAccessService.get_accessible_integrations(self.request.user)

    def get_object(self, queryset=None):
        integration = super().get_object(queryset)

        if not IntegrationAccessService.can_update_integration(
            self.request.user,
            integration,
        ):
            raise Http404

        return integration

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse("integrations:list"),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "L'intégration externe a été modifiée avec succès.",
        )

        return response
