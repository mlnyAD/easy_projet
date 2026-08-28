

from urllib.parse import urlencode

from django.contrib import messages
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views.generic import ListView

from apps.projects.models import ProjectMembership
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
from framework.viewmodel.builder import (
    ListViewModelBuilder,
)

from .form_definition import TASK_FORM_DEFINITION
from .forms import (
    TaskAssignmentFormSet,
    TaskDependencyFormSet,
    TaskForm,
)
from .lists import TASK_LIST_DEFINITION
from .models import Task


def build_task_assignment_context():
    """
    Prépare les données nécessaires à la sélection dynamique
    des personnes affectables à une tâche.
    """

    memberships = (
        ProjectMembership.objects
        .filter(
            is_active=True,
            user__is_active=True,
            project__is_active=True,
        )
        .select_related(
            "project",
            "user",
            "user__company",
            "user__job",
        )
        .order_by(
            "project__reference",
            "user__last_name",
            "user__first_name",
        )
    )

    users_data = [
        {
            "id": str(membership.user.pk),
            "project_id": str(
                membership.project.pk
            ),
            "last_name": (
                membership.user.last_name
            ),
            "first_name": (
                membership.user.first_name
            ),
            "email": membership.user.email,
            "company": str(
                membership.user.company
            ),
            "job": (
                membership.user.job.label
                if membership.user.job
                else ""
            ),
        }
        for membership in memberships
    ]

    work_packages_data = [
        {
            "id": str(work_package.pk),
            "project_id": str(
                work_package.project_id
            ),
        }
        for work_package in (
            WorkPackage.objects
            .filter(is_active=True)
            .select_related("project")
        )
    ]

    return {
        "task_users_data": users_data,
        "task_work_packages_data": (
            work_packages_data
        ),
    }


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

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        django_page = context["page_obj"]

        runtime = EPList(
            definition=TASK_LIST_DEFINITION,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(
                django_page.object_list
            ),
            page=django_page.number,
            page_size=(
                django_page.paginator.per_page
            ),
            total_items=(
                django_page.paginator.count
            ),
            total_pages=(
                django_page.paginator.num_pages
            ),
            has_previous=(
                django_page.has_previous()
            ),
            has_next=(
                django_page.has_next()
            ),
        )

        list_view = (
            ListViewModelBuilder()
            .build(
                runtime=runtime,
                page=framework_page,
            )
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité
        # avec les tests existants.
        context["list"] = list_view

        context["page_sizes"] = (
            PAGE_SIZE_VALUES
        )

        context["row_actions_template"] = (
            "tasks/task_actions.html"
        )

        context["page_title"] = "Tâches"
        context["page_subtitle"] = None
        context["page_back_url"] = None
        context["page_back_label"] = None

        context["page_action_label"] = (
            "Nouvelle tâche"
        )
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('tasks:create')}?"
            f"{urlencode({
                'next': self.request.get_full_path(),
            })}"
        )

        return context


class TaskListByWorkPackageView(
    TaskListView
):
    """
    Liste des tâches rattachées à un lot de travaux.
    """

    def get_work_package(
        self,
    ) -> WorkPackage:
        if not hasattr(
            self,
            "_work_package",
        ):
            self._work_package = (
                get_object_or_404(
                    WorkPackage.objects
                    .select_related(
                        "project",
                    ),
                    pk=self.kwargs[
                        "work_package_pk"
                    ],
                )
            )

        return self._work_package

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                work_package=(
                    self.get_work_package()
                ),
            )
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        work_package = (
            self.get_work_package()
        )
        project = work_package.project

        current_list_url = (
            self.request.get_full_path()
        )

        parent_return_url = reverse(
            "work:list-by-project",
            kwargs={
                "project_pk": project.pk,
            },
        )

        context["work_package"] = (
            work_package
        )
        context["project"] = project
        context["current_project"] = project
        context[
            "is_work_package_context"
        ] = True

        context["return_url"] = (
            current_list_url
        )

        context["parent_return_url"] = (
            parent_return_url
        )

        context["page_title"] = (
            f"Tâches du lot "
            f"{work_package.code}"
        )

        context["page_subtitle"] = (
            f"{project.reference} — "
            f"{work_package.name}"
        )

        context["page_back_url"] = (
            parent_return_url
        )
        context["page_back_label"] = (
            "Retour aux lots"
        )

        context["page_action_label"] = (
            "Nouvelle tâche"
        )
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('tasks:create')}?"
            f"{urlencode({
                'work_package': work_package.pk,
                'next': current_list_url,
            })}"
        )

        return context


class TaskFormCollectionsMixin:
    """
    Comportements communs aux formulaires de tâche.

    Ce mixin assure :
    - la navigation de retour ;
    - la construction des collections Personnel
      et Enchaînements ;
    - leur exposition à EPForm ;
    - leur validation et leur sauvegarde.
    """

    success_message = None

    def get_return_url(self):
        candidate = self.request.GET.get(
            "next"
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host()
                },
                require_https=(
                    self.request.is_secure()
                ),
            )
        ):
            return candidate

        return reverse("tasks:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_current_project(
        self,
        form=None,
    ):
        """
        Retourne le projet courant.

        La stratégie dépend du mode création
        ou modification.
        """
        raise NotImplementedError

    def get_assignment_formset(
        self,
        *,
        data=None,
        project=None,
    ):
        return TaskAssignmentFormSet(
            data=data,
            instance=self.object,
            prefix="assignments",
            project=project,
        )

    def get_dependency_formset(
        self,
        *,
        data=None,
        project=None,
    ):
        return TaskDependencyFormSet(
            data=data,
            instance=self.object,
            prefix="dependencies",
            task=self.object,
            project=project,
        )

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ) -> dict:
        """
        Retourne les collections répétables
        déclarées dans TASK_FORM_DEFINITION.
        """

        project = self.get_current_project(
            form=django_form,
        )

        data = (
            self.request.POST
            if self.request.method == "POST"
            else None
        )

        assignment_formset = context.get(
            "assignment_formset"
        )

        if assignment_formset is None:
            assignment_formset = (
                self.get_assignment_formset(
                    data=data,
                    project=project,
                )
            )

            context["assignment_formset"] = (
                assignment_formset
            )

        dependency_formset = context.get(
            "dependency_formset"
        )

        if dependency_formset is None:
            dependency_formset = (
                self.get_dependency_formset(
                    data=data,
                    project=project,
                )
            )

            context["dependency_formset"] = (
                dependency_formset
            )

        return {
            "assignments": (
                assignment_formset
            ),
            "dependencies": (
                dependency_formset
            ),
        }

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        form = context.get("form")

        project = self.get_current_project(
            form=form,
        )

        context["current_project"] = project

        context.update(
            build_task_assignment_context()
        )

        context["form_extra_template"] = (
            "tasks/task_form_script.html"
        )

        return context

    def form_valid(
        self,
        form,
    ):
        project = self.get_current_project(
            form=form,
        )

        assignment_formset = (
            self.get_assignment_formset(
                data=self.request.POST,
                project=project,
            )
        )

        dependency_formset = (
            self.get_dependency_formset(
                data=self.request.POST,
                project=project,
            )
        )

        assignment_is_valid = (
            assignment_formset.is_valid()
        )

        dependency_is_valid = (
            dependency_formset.is_valid()
        )

        if not (
            assignment_is_valid
            and dependency_is_valid
        ):
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    assignment_formset=(
                        assignment_formset
                    ),
                    dependency_formset=(
                        dependency_formset
                    ),
                )
            )

        with transaction.atomic():
            self.object = form.save()

            assignment_formset.instance = (
                self.object
            )
            assignment_formset.save()

            dependency_formset.instance = (
                self.object
            )
            dependency_formset.save()

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(
            self.get_success_url()
        )


class TaskCreateView(
    TaskFormCollectionsMixin,
    EPCreateView,
):
    model = Task
    form_class = TaskForm
    definition = TASK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "La tâche a été créée avec succès."
    )

    def get_initial(self):
        initial = super().get_initial()

        work_package_pk = (
            self.request.GET.get(
                "work_package"
            )
        )

        if work_package_pk:
            work_package = (
                WorkPackage.objects
                .filter(
                    pk=work_package_pk,
                    is_active=True,
                )
                .select_related(
                    "project"
                )
                .first()
            )

            if work_package is not None:
                initial[
                    "work_package"
                ] = work_package

        return initial

    def get_current_project(
        self,
        form=None,
    ):
        """
        Détermine le projet depuis le lot
        sélectionné dans le formulaire.
        """

        if (
            form is not None
            and hasattr(
                form,
                "cleaned_data",
            )
        ):
            work_package = (
                form.cleaned_data.get(
                    "work_package"
                )
            )

            if work_package is not None:
                return work_package.project

        work_package_pk = (
            self.request.POST.get(
                "work_package"
            )
            or self.request.GET.get(
                "work_package"
            )
        )

        if not work_package_pk:
            return None

        work_package = (
            WorkPackage.objects
            .filter(
                pk=work_package_pk,
                is_active=True,
            )
            .select_related(
                "project"
            )
            .first()
        )

        if work_package is None:
            return None

        return work_package.project


class TaskUpdateView(
    TaskFormCollectionsMixin,
    EPUpdateView,
):
    model = Task
    form_class = TaskForm
    definition = TASK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "La tâche a été modifiée avec succès."
    )

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "work_package",
                "work_package__project",
                "status",
            )
            .prefetch_related(
                "assignments",
                "assignments__user",
                "assignments__user__company",
                "assignments__user__job",
                "assignments__role",
                (
                    "assignments__role__"
                    "catalog_type"
                ),
                "predecessor_dependencies",
                (
                    "predecessor_dependencies__"
                    "predecessor"
                ),
                (
                    "predecessor_dependencies__"
                    "predecessor__work_package"
                ),
                (
                    "predecessor_dependencies__"
                    "predecessor__"
                    "work_package__project"
                ),
            )
        )

    def get_current_project(
        self,
        form=None,
    ):
        """
        Retourne le projet correspondant
        au lot actuellement sélectionné.
        """

        if (
            form is not None
            and hasattr(
                form,
                "cleaned_data",
            )
        ):
            work_package = (
                form.cleaned_data.get(
                    "work_package"
                )
            )

            if work_package is not None:
                return work_package.project

        return (
            self.object
            .work_package
            .project
        )