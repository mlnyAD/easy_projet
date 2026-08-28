

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView
from urllib.parse import urlencode

from django.contrib import messages
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

from .form_definition import WORK_PACKAGE_FORM_DEFINITION
from .forms import WorkPackageForm
from .lists import WORK_PACKAGE_LIST_DEFINITION
from .models import WorkPackage


class WorkPackageListView(ListView):
    model = WorkPackage
    template_name = "work/work_package_list.html"
    context_object_name = "work_packages"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            WorkPackage.objects
            .select_related(
                "project",
                "manager",
                "status",
            )
            .order_by(
                "project__reference",
                "code",
                "name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=WORK_PACKAGE_LIST_DEFINITION,
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
            "work/work_package_actions.html"
        )

        context["is_project_context"] = False
        context["return_url"] = self.request.get_full_path()

        context["page_title"] = "Lots de travaux"
        context["page_subtitle"] = None
        context["page_back_url"] = None
        context["page_back_label"] = None

        context["page_action_label"] = "Nouveau lot de travaux"
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('work:create')}?"
            f"{urlencode({
                'next': self.request.get_full_path(),
            })}"
        )

        return context


class WorkPackageListByProjectView(WorkPackageListView):
    """
    Liste des lots de travaux appartenant à un projet donné.
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

        project_workspace_url = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

        context["project"] = project
        context["current_project"] = project
        context["is_project_context"] = True
        context["return_url"] = project_workspace_url

        context["page_title"] = (
            "Lots de travaux du projet"
        )
        context["page_subtitle"] = (
            f"{project.reference} — {project.name}"
        )

        context["page_back_url"] = project_workspace_url
        context["page_back_label"] = "Retour au projet"

        context["page_action_label"] = (
            "Nouveau lot de travaux"
        )
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('work:create')}?"
            f"{urlencode({
                'project': project.pk,
                'next': project_workspace_url,
            })}"
        )

        return context


class WorkPackageCreateView(EPCreateView):
    model = WorkPackage
    form_class = WorkPackageForm
    definition = WORK_PACKAGE_FORM_DEFINITION
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

        return reverse_lazy("work:list")

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
            "Le lot de travaux a été créé avec succès.",
        )

        return response


class WorkPackageUpdateView(EPUpdateView):
    model = WorkPackage
    form_class = WorkPackageForm
    definition = WORK_PACKAGE_FORM_DEFINITION
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

        return reverse_lazy("work:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le lot de travaux a été modifié avec succès.",
        )

        return response