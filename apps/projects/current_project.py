

from __future__ import annotations

from django.http import HttpRequest

from apps.projects.models import Project


CURRENT_PROJECT_SESSION_KEY = (
    "easy_projet_current_project_id"
)


def set_current_project(
    request: HttpRequest,
    project: Project,
) -> None:
    """
    Définit le projet courant de l'utilisateur.

    Le projet est mémorisé dans la session afin de rester
    disponible lors de la navigation dans l'application.
    """

    request.session[
        CURRENT_PROJECT_SESSION_KEY
    ] = str(
        project.pk
    )


def clear_current_project(
    request: HttpRequest,
) -> None:
    """
    Supprime le projet courant de la session.
    """

    request.session.pop(
        CURRENT_PROJECT_SESSION_KEY,
        None,
    )