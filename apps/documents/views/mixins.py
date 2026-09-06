

from __future__ import annotations

from django.shortcuts import get_object_or_404

from apps.projects.services.access import (
    ProjectAccessService,
)


class ProjectDocumentAccessMixin:
    """
    Fournit le projet accessible à l'utilisateur courant
    pour les vues documentaires liées à un projet.
    """

    def get_project(
        self,
        *,
        project_id=None,
    ):
        if project_id is None:
            project_id = self.kwargs["project_id"]

        return get_object_or_404(
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            ),
            pk=project_id,
        )