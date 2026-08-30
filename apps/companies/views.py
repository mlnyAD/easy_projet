

from django.contrib import messages
from django.urls import reverse_lazy
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

from .form_definition import COMPANY_FORM_DEFINITION
from .forms import CompanyForm
from .lists import COMPANY_LIST_DEFINITION
from .models import Company


class CompanyListView(
    EPListPaginationMixin,
    ListView,
):
    model = Company
    template_name = "companies/company_list.html"
    context_object_name = "companies"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=COMPANY_LIST_DEFINITION,
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

        # Alias temporaire pour compatibilité avec les tests existants.
        context["list"] = list_view

        context["row_actions_template"] = (
            "companies/company_actions.html"
        )

        return context


class CompanyCreateView(EPCreateView):
    model = Company
    form_class = CompanyForm
    definition = COMPANY_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("companies:list")
    cancel_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été créée avec succès.",
        )

        return response


class CompanyUpdateView(EPUpdateView):
    model = Company
    form_class = CompanyForm
    definition = COMPANY_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("companies:list")
    cancel_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La société a été modifiée avec succès.",
        )

        return response