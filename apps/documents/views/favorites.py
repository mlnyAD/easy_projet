

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.documents.models import DocumentFavorite


class DocumentFavoriteListView(
    LoginRequiredMixin,
    ListView,
):
    """
    Liste des documents favoris de l'utilisateur connecté.
    """

    model = DocumentFavorite
    template_name = "documents/favorites/list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        return (
            DocumentFavorite.objects
            .filter(
                user=self.request.user,
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