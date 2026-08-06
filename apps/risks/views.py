

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from apps.projects.models import Project
from common.constants import (
    DEFAULT_PAGE_SIZE,
    PAGE_SIZE_VALUES,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import RISK_FORM_DEFINITION
from .forms import RiskForm
from .lists import RISK_LIST_DEFINITION
from .models import Risk


class RiskListView(ListView):
    """
    Liste globale des risques et opportunités.
    """

    model = Risk
    template_name = "risks/risk_list.html"
    context_object_name = "risks"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            Risk.objects
            .select_related(
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
            .order_by(
                "project__reference",
                "reference",
                "title",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=RISK_LIST_DEFINITION,
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

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité avec les tests existants.
        context["list"] = list_view

        context["page_sizes"] = PAGE_SIZE_VALUES
        context["row_actions_template"] = (
            "risks/risk_actions.html"
        )

        context["is_project_context"] = False
        context["return_url"] = self.request.get_full_path()

        return context


class RiskListByProjectView(RiskListView):
    """
    Liste des risques et opportunités d'un projet donné.
    """

    def get_project(self) -> Project:
        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                Project.objects.select_related(
                    "owner_company",
                    "project_manager",
                    "status",
                ),
                pk=self.kwargs["project_pk"],
            )

        return self._project

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                project=self.get_project(),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project
        context["current_project"] = project
        context["is_project_context"] = True

        # Après création ou modification, retour au résumé projet.
        context["return_url"] = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

        return context


class RiskCreateView(EPCreateView):
    model = Risk
    form_class = RiskForm
    definition = RISK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_return_url(self):
        candidate = self.request.GET.get("next")

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={self.request.get_host()},
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse_lazy("risks:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_initial(self):
        initial = super().get_initial()

        project_pk = self.request.GET.get("project")

        if project_pk:
            project = (
                Project.objects
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

    def get_return_url(self):
        candidate = self.request.GET.get("next")

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={self.request.get_host()},
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse_lazy("risks:list")

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