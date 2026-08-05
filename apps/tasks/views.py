from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView

from apps.work.models import WorkPackage
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

from .form_definition import TASK_FORM_DEFINITION
from .forms import TaskForm
from .lists import TASK_LIST_DEFINITION
from .models import Task


class TaskListView(ListView):
    """
    Liste globale des tâches.
    """

    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "work_package",
                "work_package__project",
                "status",
            )
            .order_by(
                "work_package__project__reference",
                "work_package__code",
                "code",
                "name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=TASK_LIST_DEFINITION,
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
            "tasks/task_actions.html"
        )

        return context


class TaskListByWorkPackageView(TaskListView):
    """
    Liste des tâches rattachées à un lot de travaux.
    """

    def get_work_package(self) -> WorkPackage:
        if not hasattr(self, "_work_package"):
            self._work_package = get_object_or_404(
                WorkPackage.objects.select_related(
                    "project",
                ),
                pk=self.kwargs["work_package_pk"],
            )

        return self._work_package

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                work_package=self.get_work_package(),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["work_package"] = self.get_work_package()
        context["is_work_package_context"] = True

        return context


class TaskCreateView(EPCreateView):
    model = Task
    form_class = TaskForm
    definition = TASK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("tasks:list")
    cancel_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La tâche a été créée avec succès.",
        )

        return response


class TaskUpdateView(EPUpdateView):
    model = Task
    form_class = TaskForm
    definition = TASK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("tasks:list")
    cancel_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La tâche a été modifiée avec succès.",
        )

        return response