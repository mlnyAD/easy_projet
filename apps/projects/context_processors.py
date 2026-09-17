

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

    Certains rendus techniques du framework utilisent une requête
    sans session ni utilisateur authentifié.
    """

    session = getattr(
        request,
        "session",
        None,
    )

    user = getattr(
        request,
        "user",
        None,
    )

    if (
        session is None
        or user is None
        or not user.is_authenticated
    ):
        return {
            "current_project": None,
        }

    project_id = session.get(
        CURRENT_PROJECT_SESSION_KEY
    )

    if not project_id:
        return {
            "current_project": None,
        }

    project = (
        ProjectAccessService
        .get_accessible_projects(user)
        .filter(
            pk=project_id,
        )
        .select_related(
            "company",
            "owner_company",
            "status",
        )
        .first()
    )

    if project is None:
        session.pop(
            CURRENT_PROJECT_SESSION_KEY,
            None,
        )

    return {
        "current_project": project,
    }