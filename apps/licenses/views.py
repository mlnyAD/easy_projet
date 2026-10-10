

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from urllib.parse import quote
from uuid import UUID
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views.generic import (
    DetailView,
    ListView,
)
from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
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
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from .form_definition import (
    LICENSE_FORM_DEFINITION,
)
from .forms import LicenseForm
from .lists import LICENSE_LIST_DEFINITION
from .models import License
from .services.access import LicenseAccessService


class LicenseListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    model = License

    template_name = "licenses/license_list.html"

    context_object_name = "licenses"

    list_definition = LICENSE_LIST_DEFINITION

    company_parameter = "company"
    status_parameter = "status"
    expiration_parameter = "expiration"

    expiration_all = "all"
    expiration_valid = "valid"
    expiration_expired = "expired"

    expiration_values = (
        expiration_all,
        expiration_valid,
        expiration_expired,
    )

    def get_sort_field_map(self) -> dict[str, str]:
        """
        Associe les colonnes calculées aux champs ORM triables.
        """

        sort_field_map = super().get_sort_field_map()

        sort_field_map.update(
            {
                "company_name": (
                    "client_environment__company__name"
                ),
                "status_label": "status__sort_order",
            }
        )

        return sort_field_map

    def get_license_scope(self):
        """
        Retourne les licences accessibles avant application des filtres.
        """

        return LicenseAccessService.get_accessible_licenses(
            self.request.user,
        )

    def get_filter_companies(self):
        company_ids = (
            self.get_license_scope()
            .values_list(
                "client_environment__company_id",
                flat=True,
            )
        )

        return Company.objects.filter(
            pk__in=company_ids,
        ).order_by(
            "name",
        )

    def get_filter_statuses(self):
        status_ids = (
            self.get_license_scope()
            .values_list(
                "status_id",
                flat=True,
            )
        )

        return CatalogValue.objects.filter(
            pk__in=status_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_company_filter(self) -> str | None:
        raw_company_id = self.request.GET.get(
            self.company_parameter,
            "",
        ).strip()

        if not raw_company_id:
            return None

        try:
            company_id = UUID(raw_company_id)
        except ValueError:
            return None

        if not self.get_filter_companies().filter(
            pk=company_id,
        ).exists():
            return None

        return str(company_id)

    def get_status_filter(self) -> int | None:
        raw_status_id = self.request.GET.get(
            self.status_parameter,
            "",
        ).strip()

        if not raw_status_id:
            return None

        try:
            status_id = int(raw_status_id)
        except ValueError:
            return None

        if not self.get_filter_statuses().filter(
            pk=status_id,
        ).exists():
            return None

        return status_id

    def get_expiration_filter(self) -> str:
        expiration = self.request.GET.get(
            self.expiration_parameter,
            self.expiration_all,
        )

        if expiration not in self.expiration_values:
            return self.expiration_all

        return expiration

    def get_queryset(self):
        """
        Retourne les licences accessibles, filtrées et triées.
        """

        queryset = (
            super()
            .get_queryset()
            .filter(
                pk__in=self.get_license_scope(),
            )
            .select_related(
                "client_environment",
                "client_environment__company",
                "status",
            )
        )

        company_id = self.get_company_filter()

        if company_id is not None:
            queryset = queryset.filter(
                client_environment__company_id=company_id,
            )

        status_id = self.get_status_filter()

        if status_id is not None:
            queryset = queryset.filter(
                status_id=status_id,
            )

        expiration = self.get_expiration_filter()
        today = timezone.localdate()

        if expiration == self.expiration_valid:
            queryset = queryset.filter(
                Q(
                    expiration_date__isnull=True,
                )
                | Q(
                    expiration_date__gte=today,
                )
            )
        elif expiration == self.expiration_expired:
            queryset = queryset.filter(
                expiration_date__lt=today,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs,
        )

        django_page = context["page_obj"]

        runtime = EPList(
            definition=self.list_definition,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(
                django_page.object_list,
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

        context["filter_companies"] = (
            self.get_filter_companies()
        )

        context["filter_statuses"] = (
            self.get_filter_statuses()
        )

        context["company_filter"] = (
            self.get_company_filter()
        )

        context["status_filter"] = (
            self.get_status_filter()
        )

        context["license_expiration"] = (
            self.get_expiration_filter()
        )

        context["list_filters_template"] = (
            "licenses/license_list_filters.html"
        )

        context["row_actions_template"] = (
            "licenses/license_actions.html"
        )

        context["can_create_license"] = (
            LicenseAccessService.can_create_license(
                self.request.user,
            )
        )

        context["can_update_license"] = (
            LicenseAccessService.can_update_license(
                self.request.user,
            )
        )

        context["license_create_url"] = (
            f"{reverse('licenses:create')}?next="
            f"{quote(self.request.get_full_path())}"
        )

        return context
    

class LicenseReturnUrlMixin:
    """
    Préserve l'état de la liste après création ou modification.
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

        return reverse("licenses:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

        
class LicenseCreateView(
    LicenseReturnUrlMixin,
    EPCreateView,
):
    model = License
    form_class = LicenseForm
    definition = LICENSE_FORM_DEFINITION
    template_name = "edf/form/view.html"

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


class LicenseUpdateView(
    LicenseReturnUrlMixin,
    EPUpdateView,
):
    model = License
    form_class = LicenseForm
    definition = LICENSE_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def can_edit_object(self) -> bool:
        """
        L'administrateur système modifie la licence.
        Les autres utilisateurs autorisés la consultent
        dans le même formulaire, en lecture seule.
        """

        return LicenseAccessService.can_update_license(
            self.request.user,
        )

    def get_queryset(self):
        """
        La consultation comme la modification restent limitées
        aux licences accessibles à l'utilisateur connecté.
        """

        return (
            LicenseAccessService
            .get_accessible_licenses(
                self.request.user,
            )
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La licence a été modifiée avec succès.",
        )

        return response