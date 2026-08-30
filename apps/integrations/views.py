

from urllib.parse import urlencode

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import (
    EXTERNAL_INTEGRATION_FORM_DEFINITION,
)
from .forms import ExternalIntegrationForm
from .lists import EXTERNAL_INTEGRATION_LIST_DEFINITION
from .models import ExternalIntegration


def get_allowed_return_url(
    request,
    *,
    default_url,
):
    """
    Retourne l'URL de retour demandée si elle est sûre.
    """
    candidate = request.GET.get("next")

    if (
        candidate
        and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    ):
        return candidate

    return default_url


class ExternalIntegrationListView(
    EPListPaginationMixin,
    ListView,
):
    """
    Liste des intégrations externes.
    """

    model = ExternalIntegration
    template_name = "integrations/integration_list.html"
    context_object_name = "integrations"

    def get_queryset(self):
        return (
            ExternalIntegration.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "service_type",
                "provider",
                "connection_status",
            )
            .order_by(
                "client_environment__company__name",
                "service_type__sort_order",
                "priority",
                "name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=EXTERNAL_INTEGRATION_LIST_DEFINITION,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(
                django_page.object_list
            ),
            page=django_page.number,
            page_size=django_page.paginator.per_page,
            total_items=django_page.paginator.count,
            total_pages=django_page.paginator.num_pages,
            has_previous=django_page.has_previous(),
            has_next=django_page.has_next(),
        )

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité avec
        # les conventions actuelles des listes.
        context["list"] = list_view

        context["row_actions_template"] = (
            "integrations/integration_actions.html"
        )

        context["return_url"] = (
            self.request.get_full_path()
        )

        context["page_title"] = "Intégrations externes"
        context["page_subtitle"] = (
            "Applications et services externes disponibles "
            "dans les environnements clients."
        )

        context["page_back_url"] = None
        context["page_back_label"] = None

        context["page_action_label"] = (
            "Nouvelle intégration"
        )
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('integrations:create')}?"
            f"{urlencode({
                'next': self.request.get_full_path(),
            })}"
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

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse_lazy(
                "integrations:list"
            ),
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
        return (
            ExternalIntegration.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "service_type",
                "provider",
                "connection_status",
            )
        )

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse_lazy(
                "integrations:list"
            ),
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