

from django.contrib import messages
from django.core.exceptions import PermissionDenied
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
from framework.viewmodel.builder import (
    ListViewModelBuilder,
)

from .form_definition import (
    LICENSE_FORM_DEFINITION,
)
from .forms import LicenseForm
from .lists import LICENSE_LIST_DEFINITION
from .models import License
from .services.access import LicenseAccessService


class LicenseListView(
    EPListPaginationMixin,
    ListView,
):
    model = License
    template_name = "licenses/license_list.html"
    context_object_name = "licenses"

    def get_queryset(self):
        return LicenseAccessService.get_accessible_licenses(
            self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        django_page = context["page_obj"]

        runtime = EPList(
            definition=LICENSE_LIST_DEFINITION,
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
        context["list"] = list_view
        context["row_actions_template"] = (
            "licenses/license_actions.html"
        )

        context["can_create_license"] = (
            LicenseAccessService.can_create_license(
                self.request.user
            )
        )

        return context


class LicenseCreateView(EPCreateView):
    model = License
    form_class = LicenseForm
    definition = LICENSE_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("licenses:list")
    cancel_url = reverse_lazy("licenses:list")

    def dispatch(self, request, *args, **kwargs):
        if not LicenseAccessService.can_create_license(
            request.user
        ):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La licence a été créée avec succès.",
        )

        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


class LicenseUpdateView(EPUpdateView):
    model = License
    form_class = LicenseForm
    definition = LICENSE_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("licenses:list")
    cancel_url = reverse_lazy("licenses:list")

    def dispatch(self, request, *args, **kwargs):
        if not LicenseAccessService.can_update_license(
            request.user
        ):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        return (
            LicenseAccessService
            .get_accessible_licenses(
                self.request.user
            )
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La licence a été modifiée avec succès.",
        )

        return response