from urllib.parse import urlencode

from uuid import UUID

from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin

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

from apps.projects.services.access import (
    ProjectAccessService,
)

from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)

from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)

from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)

from apps.work.models import WorkPackage

from framework.form import FormMode

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)

from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)

from framework.runtime import EPList, ListPage

from framework.integrations.django.viewmodel import (
    DjangoListViewModelBuilder,
)

from apps.catalogs.models import CatalogValue

from apps.projects.models import (
    Project,
    ProjectMembership,
)

from .form_definition import TASK_FORM_DEFINITION

from .forms import (
    TaskAssignmentFormSet,
    TaskDependencyFormSet,
    TaskForm,
    TaskJobRequirementFormSet,
)

from .lists import TASK_LIST_DEFINITION

from .models import Task

from .services import TaskWorkloadService


def build_task_assignment_context(
    *,
    user,
):
    """

    Prépare les données nécessaires à la sélection dynamique

    des personnes affectables à une tâche.

    Seuls les projets sur lesquels l'utilisateur peut travailler

    sont exposés au navigateur.

    """

    workable_projects = ProjectAuthorizationService.get_workable_projects(user)

    memberships = (
        ProjectMembership.objects.filter(
            project__in=workable_projects,
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
            "project_id": str(membership.project.pk),
            "last_name": membership.user.last_name,
            "first_name": membership.user.first_name,
            "email": membership.user.email,
            "company": str(membership.user.company),
            "job": (membership.user.job.label if membership.user.job else ""),
        }
        for membership in memberships
    ]

    work_packages_data = [
        {
            "id": str(work_package.pk),
            "project_id": str(work_package.project_id),
        }
        for work_package in (
            WorkPackage.objects.filter(
                project__in=workable_projects,
                is_active=True,
            ).select_related("project")
        )
    ]

    return {
        "task_users_data": users_data,
        "task_work_packages_data": (work_packages_data),
    }


class TaskListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    """

    Liste globale des tâches.

    """

    model = Task

    template_name = "tasks/task_list.html"

    context_object_name = "tasks"

    list_definition = TASK_LIST_DEFINITION

    project_parameter = "project"

    work_package_parameter = "work_package"

    status_parameter = "status"

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

        sort_field_map.update(
            {
                "work_package": "work_package__code",
                "status": "status__sort_order",
            }
        )

        return sort_field_map

    def get_projects_for_list(self):
        """

        Retourne les projets dans le périmètre de la liste.

        """

        return ProjectAccessService.get_accessible_projects(
            self.request.user,
        )

    def get_work_packages_for_list(self):
        """

        Retourne les lots dans le périmètre de la liste.

        """

        return WorkPackage.objects.filter(
            project__in=self.get_projects_for_list(),
        )

    def get_task_scope(self):
        """

        Retourne les tâches accessibles avant application des filtres.

        """

        return Task.objects.filter(
            work_package__in=(self.get_work_packages_for_list()),
        ).select_related(
            "work_package",
            "work_package__project",
            "status",
        )

    def get_filter_projects(self):

        project_ids = self.get_task_scope().values_list(
            "work_package__project_id",
            flat=True,
        )

        return Project.objects.filter(
            pk__in=project_ids,
        ).order_by(
            "reference",
            "name",
        )

    def get_filter_work_packages(self):

        work_package_ids = self.get_task_scope().values_list(
            "work_package_id",
            flat=True,
        )

        return (
            WorkPackage.objects.filter(
                pk__in=work_package_ids,
            )
            .select_related(
                "project",
            )
            .order_by(
                "project__reference",
                "code",
                "name",
            )
        )

    def get_filter_statuses(self):

        status_ids = self.get_task_scope().values_list(
            "status_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=status_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_project_filter(self) -> str | None:

        raw_project_id = self.request.GET.get(
            self.project_parameter,
            "",
        ).strip()

        if not raw_project_id:
            return None

        try:
            project_id = UUID(raw_project_id)

        except ValueError:
            return None

        if (
            not self.get_filter_projects()
            .filter(
                pk=project_id,
            )
            .exists()
        ):
            return None

        return str(project_id)

    def get_work_package_filter(self) -> str | None:

        raw_work_package_id = self.request.GET.get(
            self.work_package_parameter,
            "",
        ).strip()

        if not raw_work_package_id:
            return None

        try:
            work_package_id = UUID(raw_work_package_id)

        except ValueError:
            return None

        if (
            not self.get_filter_work_packages()
            .filter(
                pk=work_package_id,
            )
            .exists()
        ):
            return None

        return str(work_package_id)

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

        if (
            not self.get_filter_statuses()
            .filter(
                pk=status_id,
            )
            .exists()
        ):
            return None

        return status_id

    def get_activity_filter(self) -> str:

        activity = self.request.GET.get(
            self.activity_parameter,
            self.activity_active,
        )

        if activity not in self.activity_values:
            return self.activity_active

        return activity

    def get_queryset(self):
        """

        Retourne les tâches accessibles, filtrées et triées.

        """

        queryset = (
            super()
            .get_queryset()
            .filter(
                work_package__in=(self.get_work_packages_for_list()),
            )
            .select_related(
                "work_package",
                "work_package__project",
                "status",
            )
        )

        project_id = self.get_project_filter()

        if project_id is not None:
            queryset = queryset.filter(
                work_package__project_id=project_id,
            )

        work_package_id = self.get_work_package_filter()

        if work_package_id is not None:
            queryset = queryset.filter(
                work_package_id=work_package_id,
            )

        status_id = self.get_status_filter()

        if status_id is not None:
            queryset = queryset.filter(
                status_id=status_id,
            )

        activity = self.get_activity_filter()

        if activity != self.activity_all:
            queryset = queryset.filter(
                is_active=(activity == self.activity_active),
            )

        return queryset

    def get_context_data(
        self,
        **kwargs,
    ):

        context = super().get_context_data(
            **kwargs,
        )

        django_page = context["page_obj"]

        page_tasks = tuple(
            django_page.object_list,
        )

        consumed_hours_by_task = TaskWorkloadService.get_consumed_hours_by_task(
            task_ids=(task.pk for task in page_tasks),
        )

        workable_projects = ProjectAuthorizationService.get_workable_projects(
            self.request.user,
        )

        workable_project_ids = set(
            workable_projects.filter(
                pk__in={task.work_package.project_id for task in page_tasks},
            ).values_list(
                "pk",
                flat=True,
            )
        )

        for task in page_tasks:
            task.consumed_workload_hours = consumed_hours_by_task.get(
                task.pk,
                TaskWorkloadService.ZERO_HOURS,
            )

            task.can_work = task.work_package.project_id in workable_project_ids

        runtime = EPList(
            definition=self.list_definition,
            rows=page_tasks,
        )

        framework_page = ListPage(
            rows=page_tasks,
            page=django_page.number,
            page_size=django_page.paginator.per_page,
            total_items=django_page.paginator.count,
            total_pages=django_page.paginator.num_pages,
            has_previous=django_page.has_previous(),
            has_next=django_page.has_next(),
        )

        visible_column_identifiers = self.get_visible_column_identifiers()

        sort_by = self.get_sort_by()

        sort_descending = self.get_sort_descending()

        list_view = DjangoListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(visible_column_identifiers),
        )

        context["list_view"] = list_view

        context["list"] = list_view

        context["list_definition"] = self.get_list_definition()

        context["visible_column_identifiers"] = visible_column_identifiers

        context["can_save_list_preferences"] = self.request.user.is_authenticated

        context["sort_by"] = sort_by

        context["sort_descending"] = sort_descending

        context["filter_projects"] = self.get_filter_projects()

        context["filter_work_packages"] = self.get_filter_work_packages()

        context["filter_statuses"] = self.get_filter_statuses()

        context["project_filter"] = self.get_project_filter()

        context["work_package_filter"] = self.get_work_package_filter()

        context["status_filter"] = self.get_status_filter()

        context["task_activity"] = self.get_activity_filter()

        context["list_filters_template"] = "tasks/task_list_filters.html"

        context["row_actions_template"] = "tasks/task_actions.html"

        context["is_work_package_context"] = False

        context["page_title"] = "Tâches"

        context["page_subtitle"] = None

        context["page_back_url"] = None

        context["page_back_label"] = None

        context["return_url"] = self.request.get_full_path()

        if workable_projects.exists():
            context["page_action_label"] = "Nouvelle tâche"

            context["page_action_icon"] = "plus"

            context["page_action_url"] = (
                f"{reverse('tasks:create')}?"
                f"{urlencode({'next': self.request.get_full_path()})}"
            )

        else:
            context["page_action_label"] = None

            context["page_action_icon"] = None

            context["page_action_url"] = None

        return context


class TaskListByWorkPackageView(TaskListView):
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
            accessible_projects = ProjectAccessService.get_accessible_projects(
                self.request.user
            )

            self._work_package = get_object_or_404(
                WorkPackage.objects.filter(
                    project__in=(accessible_projects),
                ).select_related(
                    "project",
                ),
                pk=self.kwargs["work_package_pk"],
            )

        return self._work_package

    def get_work_packages_for_list(self):
        """

        Restreint la liste et ses filtres au lot courant.

        """

        return WorkPackage.objects.filter(
            pk=self.get_work_package().pk,
        )

    def get_context_data(
        self,
        **kwargs,
    ):

        context = super().get_context_data(**kwargs)

        work_package = self.get_work_package()

        project = work_package.project

        current_list_url = self.request.get_full_path()

        parent_return_url = reverse(
            "work:list-by-project",
            kwargs={
                "project_pk": project.pk,
            },
        )

        can_work_on_project = ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=project,
        )

        context["work_package"] = work_package

        context["project"] = project

        context["current_project"] = project

        context["is_work_package_context"] = True

        context["can_work_on_project"] = can_work_on_project

        context["return_url"] = current_list_url

        context["parent_return_url"] = parent_return_url

        context["page_title"] = f"Tâches du lot {work_package.code}"

        context["page_subtitle"] = f"{project.reference} — {work_package.name}"

        context["page_back_url"] = parent_return_url

        context["page_back_label"] = "Retour aux lots"

        if can_work_on_project:
            context["page_action_label"] = "Nouvelle tâche"

            context["page_action_icon"] = "plus"

            context["page_action_url"] = (
                f"{reverse('tasks:create')}?"
                f"{
                    urlencode(
                        {
                            'work_package': work_package.pk,
                            'next': current_list_url,
                        }
                    )
                }"
            )

        else:
            context["page_action_label"] = None

            context["page_action_icon"] = None

            context["page_action_url"] = None

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

        candidate = self.request.GET.get("next")

        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=(self.request.is_secure()),
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

    def get_job_requirement_formset(
        self,
        *,
        data=None,
    ):
        if (
            data is not None
            and "job_requirements-TOTAL_FORMS" not in data
        ):
            data = None

        return TaskJobRequirementFormSet(
            data=data,
            instance=self.object,
            prefix="job_requirements",
        )
        
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

        Retourne les collections répétables déclarées dans

        TASK_FORM_DEFINITION.

        """

        project = self.get_current_project(
            form=django_form,
        )

        data = self.request.POST if self.request.method == "POST" else None

        job_requirement_formset = context.get("job_requirement_formset")

        if job_requirement_formset is None:
            job_requirement_formset = self.get_job_requirement_formset(
                data=data,
            )

            context["job_requirement_formset"] = job_requirement_formset

        assignment_formset = context.get("assignment_formset")

        if assignment_formset is None:
            assignment_formset = self.get_assignment_formset(
                data=data,
                project=project,
            )

            context["assignment_formset"] = assignment_formset

        dependency_formset = context.get("dependency_formset")

        if dependency_formset is None:
            dependency_formset = self.get_dependency_formset(
                data=data,
                project=project,
            )

            context["dependency_formset"] = dependency_formset

        return {
            "job_requirements": job_requirement_formset,
            "assignments": assignment_formset,
            "dependencies": dependency_formset,
        }

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_context_data(
        self,
        **kwargs,
    ):

        context = super().get_context_data(**kwargs)

        form = context.get("form")

        project = self.get_current_project(
            form=form,
        )

        context["current_project"] = project

        if self.get_form_mode() is not FormMode.READONLY:
            context.update(
                build_task_assignment_context(
                    user=self.request.user,
                )
            )

            context["form_extra_template"] = "tasks/task_form_script.html"

        return context

    def form_valid(
        self,
        form,
    ):

        project = self.get_current_project(
            form=form,
        )

        job_requirement_formset = self.get_job_requirement_formset(
            data=self.request.POST,
        )

        assignment_formset = self.get_assignment_formset(
            data=self.request.POST,
            project=project,
        )

        dependency_formset = self.get_dependency_formset(
            data=self.request.POST,
            project=project,
        )

        job_requirement_is_valid = (
            not job_requirement_formset.is_bound
            or job_requirement_formset.is_valid()
        )

        assignment_is_valid = assignment_formset.is_valid()

        dependency_is_valid = dependency_formset.is_valid()

        if not (
            job_requirement_is_valid and assignment_is_valid and dependency_is_valid
        ):
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    job_requirement_formset=(job_requirement_formset),
                    assignment_formset=assignment_formset,
                    dependency_formset=dependency_formset,
                )
            )

        with transaction.atomic():
            self.object = form.save()

            if job_requirement_formset.is_bound:
                job_requirement_formset.instance = self.object

            job_requirement_formset.save()
    
            assignment_formset.instance = self.object

            assignment_formset.save()

            dependency_formset.instance = self.object

            dependency_formset.save()

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(self.get_success_url())


class TaskCreateView(
    UserPassesTestMixin,
    TaskFormCollectionsMixin,
    EPCreateView,
):
    model = Task

    form_class = TaskForm

    definition = TASK_FORM_DEFINITION

    template_name = "edf/form/view.html"

    success_message = "La tâche a été créée avec succès."

    def test_func(self):

        return ProjectAuthorizationService.get_workable_projects(
            self.request.user
        ).exists()

    def get_initial(self):

        initial = super().get_initial()

        work_package_pk = self.request.GET.get("work_package")

        if work_package_pk:
            workable_projects = ProjectAuthorizationService.get_workable_projects(
                self.request.user
            )

            work_package = (
                WorkPackage.objects.filter(
                    pk=work_package_pk,
                    project__in=workable_projects,
                    is_active=True,
                )
                .select_related("project")
                .first()
            )

            if work_package is not None:
                initial["work_package"] = work_package

        return initial

    def get_current_project(
        self,
        form=None,
    ):
        """

        Détermine le projet depuis le lot

        sélectionné dans le formulaire.

        """

        if form is not None and hasattr(
            form,
            "cleaned_data",
        ):
            work_package = form.cleaned_data.get("work_package")

            if work_package is not None:
                return work_package.project

        work_package_pk = self.request.POST.get("work_package") or self.request.GET.get(
            "work_package"
        )

        if not work_package_pk:
            return None

        workable_projects = ProjectAuthorizationService.get_workable_projects(
            self.request.user
        )

        work_package = (
            WorkPackage.objects.filter(
                pk=work_package_pk,
                project__in=workable_projects,
                is_active=True,
            )
            .select_related("project")
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

    success_message = "La tâche a été modifiée avec succès."

    def get_queryset(self):

        accessible_projects = ProjectAccessService.get_accessible_projects(
            self.request.user
        )

        return (
            Task.objects.filter(
                work_package__project__in=(accessible_projects),
            )
            .select_related(
                "work_package",
                "work_package__project",
                "status",
            )
            .prefetch_related(
                "job_requirements",
                "job_requirements__job",
                "job_requirements__job__catalog_type",
                "assignments",
                "assignments__user",
                "assignments__user__company",
                "assignments__user__job",
                "assignments__role",
                ("assignments__role__catalog_type"),
                "predecessor_dependencies",
                ("predecessor_dependencies__predecessor"),
                ("predecessor_dependencies__predecessor__work_package"),
                ("predecessor_dependencies__predecessor__work_package__project"),
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

        if form is not None and hasattr(
            form,
            "cleaned_data",
        ):
            work_package = form.cleaned_data.get("work_package")

            if work_package is not None:
                return work_package.project

        return self.object.work_package.project

    def can_edit_object(self) -> bool:
        """

        Indique si l'utilisateur peut modifier la tâche courante.

        L'utilisateur qui peut seulement consulter le projet ouvre

        la tâche en lecture seule.

        """

        return ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=(self.object.work_package.project),
        )
