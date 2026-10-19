

from __future__ import annotations

from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.documents.models import (
    DocumentFavorite,
    DocumentFolder,
)
from apps.projects.services.access import (
    ProjectAccessService,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)


class DocumentFavoriteListView(
    LoginRequiredMixin,
    ListView,
):
    """
    Liste les documents favoris accessibles à l'utilisateur connecté.
    """

    model = DocumentFavorite
    template_name = "documents/favorites/list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
        )

        return (
            DocumentFavorite.objects
            .filter(
                user=self.request.user,
                document__project__in=accessible_projects,
                document__trashed_at__isnull=True,
            )
            .select_related(
                "document",
                "document__project",
                "document__folder",
                "document__current_version",
            )
            .order_by(
                "document__project__name",
                "document__title",
            )
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        favorites = tuple(
            context["favorites"]
        )

        projects_by_id = {
            favorite.document.project_id: (
                favorite.document.project
            )
            for favorite in favorites
        }

        project_ids = set(
            projects_by_id
        )

        work_project_ids = {
            project_id
            for project_id, project in (
                projects_by_id.items()
            )
            if ProjectAuthorizationService.can_work_on_project(
                user=self.request.user,
                project=project,
            )
        }
        
        folders_by_project_id = defaultdict(list)

        folders = (
            DocumentFolder.objects
            .filter(
                project_id__in=project_ids,
                is_active=True,
                is_doe_root=False,
                is_doe_generated=False,
            )
            .order_by(
                "project_id",
                "sort_order",
                "name",
            )
        )

        for folder in folders:
            folders_by_project_id[
                folder.project_id
            ].append(folder)

        for favorite in favorites:
            document = favorite.document

            document.can_work_on_project = (
                document.project_id
                in work_project_ids
            )

            document.destination_folders = tuple(
                folders_by_project_id[
                    document.project_id
                ]
            )

        context.update(
            {
                "favorites": favorites,
                "destination_folders": (),
                "return_url": (
                    self.request.get_full_path()
                ),
            }
        )

        return context