

from __future__ import annotations

from apps.projects.services.access import (
    ProjectAccessService,
)

from .current_project import (
    CURRENT_PROJECT_SESSION_KEY,
)


def current_project(request):
    """
    Expose le projet courant dans tous les templates.

    Le projet courant est conservé dans la session utilisateur.

    Si le projet enregistré n'existe plus ou n'est plus accessible,
    la valeur de session est supprimée.
    """

    project_id = request.session.get(
        CURRENT_PROJECT_SESSION_KEY
    )

    if not project_id:
        return {
            "current_project": None,
        }

    if not request.user.is_authenticated:
        return {
            "current_project": None,
        }

    project = (
        ProjectAccessService
        .get_accessible_projects(
            request.user
        )
        .filter(
            pk=project_id,
        )
        .select_related(
            "company",
            "owner_company",
            "project_manager",
            "status",
        )
        .first()
    )

    if project is None:
        request.session.pop(
            CURRENT_PROJECT_SESSION_KEY,
            None,
        )

    return {
        "current_project": project,
    }