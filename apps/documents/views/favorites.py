

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.documents.models import DocumentFavorite
from apps.projects.services.access import (
    ProjectAccessService,
)


class DocumentFavoriteListView(
    LoginRequiredMixin,
    ListView,
):
    """
    Liste des documents favoris accessibles
    à l'utilisateur connecté.
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
                document__project__in=(
                    accessible_projects
                ),
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