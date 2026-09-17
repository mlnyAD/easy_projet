

from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.projects.services.access import (
    ProjectAccessService,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)


class ProjectDocumentAccessMixin:
    """
    Fournit le projet visible par l'utilisateur courant
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


class ProjectDocumentWorkMixin(
    ProjectDocumentAccessMixin,
):
    """
    Réserve les opérations d'écriture documentaire aux
    utilisateurs pouvant travailler sur le projet.
    """

    def get_project(
        self,
        *,
        project_id=None,
    ):
        project = super().get_project(
            project_id=project_id,
        )

        if not (
            ProjectAuthorizationService
            .can_work_on_project(
                user=self.request.user,
                project=project,
            )
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas modifier les documents "
                "de ce projet."
            )

        return project