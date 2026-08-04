

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView

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

from .form_definition import PROJECT_FORM_DEFINITION
from .forms import ProjectForm
from .lists import PROJECT_LIST_DEFINITION
from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "company",
                "project_manager",
                "status",
            )
            .order_by(
                "reference",
                "name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=PROJECT_LIST_DEFINITION,
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
            "projects/project_actions.html"
        )

        return context


class ProjectCreateView(EPCreateView):
    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("projects:list")
    cancel_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le projet a été créé avec succès.",
        )

        return response


class ProjectUpdateView(EPUpdateView):
    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("projects:list")
    cancel_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le projet a été modifié avec succès.",
        )

        return response