from urllib.parse import urlencode

from uuid import UUID
from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin

from django.shortcuts import get_object_or_404

from django.urls import reverse

from django.utils.http import url_has_allowed_host_and_scheme

from django.views.generic import ListView

from apps.catalogs.models import CatalogValue
from apps.users.models import User

from apps.projects.models import Project

from apps.projects.services.access import ProjectAccessService

from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)

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


from .form_definition import WORK_PACKAGE_FORM_DEFINITION

from .forms import WorkPackageForm

from .lists import WORK_PACKAGE_LIST_DEFINITION

from .models import WorkPackage
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)


class WorkPackageListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    model = WorkPackage

    template_name = "work/work_package_list.html"

    context_object_name = "work_packages"

    list_definition = WORK_PACKAGE_LIST_DEFINITION

    project_parameter = "project"
    manager_parameter = "manager"
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
                "project": "project__reference",
                "manager": "manager__last_name",
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

    def get_work_package_scope(self):
        """
        Retourne les lots accessibles avant application des filtres.
        """

        return (
            WorkPackage.objects.filter(
                project__in=self.get_projects_for_list(),
            )
            .select_related(
                "project",
                "manager",
                "status",
            )
        )

    def get_filter_projects(self):
        """
        Retourne les projets réellement présents dans la liste.
        """

        project_ids = (
            self.get_work_package_scope()
            .values_list(
                "project_id",
                flat=True,
            )
        )

        return Project.objects.filter(
            pk__in=project_ids,
        ).order_by(
            "reference",
            "name",
        )

    def get_filter_managers(self):
        """
        Retourne les responsables réellement présents dans la liste.
        """

        manager_ids = (
            self.get_work_package_scope()
            .exclude(
                manager__isnull=True,
            )
            .values_list(
                "manager_id",
                flat=True,
            )
        )

        return User.objects.filter(
            pk__in=manager_ids,
        ).order_by(
            "last_name",
            "first_name",
        )

    def get_filter_statuses(self):
        """
        Retourne les statuts réellement présents dans la liste.
        """

        status_ids = (
            self.get_work_package_scope()
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

        if not self.get_filter_projects().filter(
            pk=project_id,
        ).exists():
            return None

        return str(project_id)

    def get_manager_filter(self) -> str | None:
        raw_manager_id = self.request.GET.get(
            self.manager_parameter,
            "",
        ).strip()

        if not raw_manager_id:
            return None

        try:
            manager_id = UUID(raw_manager_id)
        except ValueError:
            return None

        if not self.get_filter_managers().filter(
            pk=manager_id,
        ).exists():
            return None

        return str(manager_id)

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
        Retourne les lots accessibles, filtrés et triés.
        """

        queryset = (
            super()
            .get_queryset()
            .filter(
                project__in=self.get_projects_for_list(),
            )
            .select_related(
                "project",
                "manager",
                "status",
            )
        )

        project_id = self.get_project_filter()

        if project_id is not None:
            queryset = queryset.filter(
                project_id=project_id,
            )

        manager_id = self.get_manager_filter()

        if manager_id is not None:
            queryset = queryset.filter(
                manager_id=manager_id,
            )

        status_id = self.get_status_filter()

        if status_id is not None:
            queryset = queryset.filter(
                status_id=status_id,
            )

        activity = self.get_activity_filter()

        if activity != self.activity_all:
            queryset = queryset.filter(
                is_active=(
                    activity == self.activity_active
                ),
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs,
        )

        django_page = context["page_obj"]

        page_work_packages = tuple(
            django_page.object_list,
        )

        administrable_projects = (
            ProjectAuthorizationService
            .get_administrable_projects(
                self.request.user,
            )
        )

        administrable_project_ids = set(
            administrable_projects.filter(
                pk__in={
                    work_package.project_id
                    for work_package in page_work_packages
                },
            )
            .values_list(
                "pk",
                flat=True,
            )
        )

        for work_package in page_work_packages:
            work_package.can_administer = (
                work_package.project_id
                in administrable_project_ids
            )

        runtime = EPList(
            definition=self.list_definition,
            rows=page_work_packages,
        )

        framework_page = ListPage(
            rows=page_work_packages,
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

        list_view = (
            DjangoListViewModelBuilder()
            .build(
                runtime=runtime,
                page=framework_page,
                sort_by=sort_by,
                descending=sort_descending,
                visible_column_identifiers=(
                    visible_column_identifiers
                ),
            )
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

        context["filter_projects"] = (
            self.get_filter_projects()
        )

        context["filter_managers"] = (
            self.get_filter_managers()
        )

        context["filter_statuses"] = (
            self.get_filter_statuses()
        )

        context["project_filter"] = (
            self.get_project_filter()
        )

        context["manager_filter"] = (
            self.get_manager_filter()
        )

        context["status_filter"] = (
            self.get_status_filter()
        )

        context["work_package_activity"] = (
            self.get_activity_filter()
        )

        context["list_filters_template"] = (
            "work/work_package_list_filters.html"
        )

        context["row_actions_template"] = (
            "work/work_package_actions.html"
        )

        context["is_project_context"] = False

        context["return_url"] = (
            self.request.get_full_path()
        )

        context["page_title"] = "Lots de travaux"
        context["page_subtitle"] = None
        context["page_back_url"] = None
        context["page_back_label"] = None

        if administrable_projects.exists():
            context["page_action_label"] = (
                "Nouveau lot de travaux"
            )
            context["page_action_icon"] = "plus"
            context["page_action_url"] = (
                f"{reverse('work:create')}?"
                f"{urlencode({'next': self.request.get_full_path()})}"
            )
        else:
            context["page_action_label"] = None
            context["page_action_icon"] = None
            context["page_action_url"] = None

        return context
    

class WorkPackageListByProjectView(WorkPackageListView):
    """

    Liste des lots de travaux appartenant à un projet donné.

    """

    def get_project(self) -> Project:

        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                ProjectAccessService.get_accessible_projects(
                    self.request.user
                ).select_related(
                    "owner_company",
                    "status",
                ),
                pk=self.kwargs["project_pk"],
            )

        return self._project

    def get_projects_for_list(self):
        """
        Restreint la liste et ses filtres au projet courant.
        """

        return (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user,
            )
            .filter(
                pk=self.get_project().pk,
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

        can_administer_project = ProjectAuthorizationService.can_administer_project(
            user=self.request.user,
            project=project,
        )

        context["project"] = project

        context["current_project"] = project

        context["is_project_context"] = True

        context["can_administer_project"] = can_administer_project

        context["return_url"] = (
            self.request.get_full_path()
        )

        context["page_title"] = "Lots de travaux du projet"

        context["page_subtitle"] = f"{project.reference} — {project.name}"

        context["page_back_url"] = project_workspace_url

        context["page_back_label"] = "Retour au projet"

        if can_administer_project:
            context["page_action_label"] = "Nouveau lot de travaux"

            context["page_action_icon"] = "plus"

            context["page_action_url"] = (
                f"{reverse('work:create')}?"
                f"{
                    urlencode(
                        {
                            'project': project.pk,
                            'next': self.request.get_full_path(),
                        }
                    )
                }"
            )

        else:
            context["page_action_label"] = None

            context["page_action_icon"] = None

            context["page_action_url"] = None

        return context


class WorkPackageCreateView(
    UserPassesTestMixin,
    EPCreateView,
):
    model = WorkPackage

    form_class = WorkPackageForm

    definition = WORK_PACKAGE_FORM_DEFINITION

    template_name = "edf/form/view.html"

    def test_func(self):

        return ProjectAuthorizationService.get_administrable_projects(
            self.request.user
        ).exists()

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_return_url(self):

        candidate = self.request.GET.get("next")

        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=(self.request.is_secure()),
        ):
            return candidate

        return reverse("work:list")

    def get_success_url(self):

        return self.get_return_url()

    def get_cancel_url(self):

        return self.get_return_url()

    def get_initial(self):

        initial = super().get_initial()

        project_pk = self.request.GET.get("project")

        if project_pk:
            project = (
                ProjectAuthorizationService.get_administrable_projects(
                    self.request.user
                )
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

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_queryset(self):

        accessible_projects = ProjectAccessService.get_accessible_projects(
            self.request.user
        )

        return WorkPackage.objects.filter(
            project__in=accessible_projects,
        ).select_related(
            "project",
            "manager",
            "status",
        )

    def can_edit_object(self) -> bool:
        """

        Indique si l'utilisateur peut administrer le lot courant.



        Un utilisateur qui peut seulement consulter le projet ouvre

        le lot en lecture seule.

        """

        return ProjectAuthorizationService.can_administer_project(
            user=self.request.user,
            project=self.object.project,
        )

    def get_return_url(self):

        candidate = self.request.GET.get("next")

        if candidate and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={self.request.get_host()},
            require_https=(self.request.is_secure()),
        ):
            return candidate

        return reverse("work:list")

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
