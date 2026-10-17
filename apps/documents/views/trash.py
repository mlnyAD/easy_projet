

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from apps.documents.lists import DOCUMENT_TRASH_LIST_DEFINITION
from apps.documents.models import Document
from apps.documents.views.mixins import (
    ProjectDocumentAccessMixin,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)


class DocumentTrashListView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    """Liste des documents source placés dans la corbeille."""

    model = Document
    template_name = "documents/document_trash.html"
    context_object_name = "documents"

    list_definition = DOCUMENT_TRASH_LIST_DEFINITION

    def get_queryset(self):
        project = self.get_project()

        return (
            super()
            .get_queryset()
            .filter(
                project=project,
                is_doe_generated=False,
                trashed_at__isnull=False,
            )
            .select_related(
                "folder",
                "current_version",
                "trashed_by",
            )
        )

    def get_sort_descending(self) -> bool:
        if self.sort_direction_parameter not in self.request.GET:
            return True

        return super().get_sort_descending()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        django_page = context["page_obj"]

        runtime = EPList(
            definition=self.list_definition,
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
            visible_column_identifiers=visible_column_identifiers,
        )

        can_work_on_project = (
            ProjectAuthorizationService.can_work_on_project(
                user=self.request.user,
                project=project,
            )
        )

        can_permanently_delete_document = (
            ProjectAuthorizationService
            .can_permanently_delete_document(
                user=self.request.user,
                project=project,
            )
        )

        context.update(
            {
                "project": project,
                "list_view": list_view,
                "list": list_view,
                "list_definition": self.get_list_definition(),
                "visible_column_identifiers": (
                    visible_column_identifiers
                ),
                "can_save_list_preferences": (
                    self.request.user.is_authenticated
                ),
                "sort_by": sort_by,
                "sort_descending": sort_descending,
                "can_work_on_project": can_work_on_project,
                "can_permanently_delete_document": (
                    can_permanently_delete_document
                ),
                "return_url": self.get_return_url(),
                "row_actions_template": (
                    "documents/document_trash_actions.html"
                    if can_work_on_project
                    else None
                ),
            }
        )

        return context
    
    def get_return_url(self) -> str | None:
        candidate = (
            self.request.GET.get("next")
            or ""
        ).strip()

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={self.request.get_host()},
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return None