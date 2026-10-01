

from django.contrib import messages
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from urllib.parse import quote
from django.views.generic import ListView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import COMPANY_FORM_DEFINITION
from .forms import CompanyForm
from .lists import COMPANY_LIST_DEFINITION
from .models import Company


class CompanyListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    model = Company
    template_name = "companies/company_list.html"
    context_object_name = "companies"

    list_definition = COMPANY_LIST_DEFINITION

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
        """
        Associe les colonnes affichées aux champs ORM triables.
        """

        sort_field_map = super().get_sort_field_map()

        sort_field_map["siret_display"] = "siret"

        return sort_field_map
    
    def get_activity_filter(self) -> str:
        """
        Retourne le filtre d'activité effectif.
        """

        activity = self.request.GET.get(
            self.activity_parameter,
            self.activity_active,
        )

        if activity not in self.activity_values:
            return self.activity_active

        return activity

    def get_queryset(self):
        """
        Retourne les sociétés filtrées puis triées.

        Le tri est appliqué par EPListSortingMixin avant la
        pagination Django.
        """

        queryset = super().get_queryset()

        activity = self.get_activity_filter()

        if activity == self.activity_all:
            return queryset

        return queryset.filter(
            is_active=(
                activity == self.activity_active
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=self.list_definition,
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

        visible_column_identifiers = (
            self.get_visible_column_identifiers()
        )

        sort_by = self.get_sort_by()
        sort_descending = self.get_sort_descending()

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(
                visible_column_identifiers
            ),
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité avec les tests existants.
        context["list"] = list_view

        context["list_definition"] = (
            self.get_list_definition()
        )

        context["visible_column_identifiers"] = (
            visible_column_identifiers
        )

        context["can_save_list_preferences"] = (
            self.request.user.is_authenticated
        )

        context["sort_by"] = sort_by
        context["sort_descending"] = sort_descending

        context["company_activity"] = (
            self.get_activity_filter()
        )

        context["list_filters_template"] = (
            "companies/company_list_filters.html"
        )

        context["row_actions_template"] = (
            "companies/company_actions.html"
        )

        context["company_create_url"] = (
            f"{reverse('companies:create')}?next="
            f"{quote(self.request.get_full_path())}"
        )

        return context


class CompanyReturnUrlMixin:
    """
    Préserve l'état de la liste lors d'une création ou modification.
    """

    def get_return_url(self):
        candidate = self.request.GET.get(
            "next",
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host(),
                },
                require_https=(
                    self.request.is_secure()
                ),
            )
        ):
            return candidate

        return reverse("companies:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()
        
class CompanyCreateView(
    CompanyReturnUrlMixin,
    EPCreateView,
):
    model = Company
    form_class = CompanyForm
    definition = COMPANY_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été créée avec succès.",
        )

        return response


class CompanyUpdateView(
    CompanyReturnUrlMixin,
    EPUpdateView,
):
    model = Company
    form_class = CompanyForm
    definition = COMPANY_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été modifiée avec succès.",
        )

        return response