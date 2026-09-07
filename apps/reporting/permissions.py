

from apps.projects.models import Project


PROJECT_ROLE_CATALOG = "USER_PROJECT_ROLE"
PROJECT_MANAGER_ROLE = "PROJECT_MANAGER"


def can_review_activity_reports(user) -> bool:
    """
    Indique si l'utilisateur possède le droit fonctionnel
    d'accéder à la validation des rapports d'activité.

    Le périmètre des projets consultables est géré
    séparément par ProjectAccessService.

    Ont ce droit :
    - l'administrateur système ;
    - l'administrateur d'au moins un environnement client actif ;
    - le chef de projet d'au moins un projet actif.
    """

    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    if user.is_system_admin:
        return True

    if (
        user.client_environment_memberships
        .filter(
            is_active=True,
            is_client_admin=True,
            client_environment__is_active=True,
        )
        .exists()
    ):
        return True

    return (
        user.project_memberships
        .filter(
            is_active=True,
            project__is_active=True,
            role__catalog_type__code=PROJECT_ROLE_CATALOG,
            role__catalog_type__is_active=True,
            role__code=PROJECT_MANAGER_ROLE,
            role__is_active=True,
        )
        .exists()
    )


def can_validate_activity_report_project(
    user,
    project: Project,
) -> bool:
    """
    Indique si l'utilisateur peut valider
    un rapport d'activité pour un projet donné.

    Ont ce droit sur le projet :
    - l'administrateur système ;
    - l'administrateur actif du ClientEnvironment
      auquel appartient le projet ;
    - le chef de projet actif de ce projet.
    """

    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    if not project.is_active:
        return False

    if user.is_system_admin:
        return True

    if (
        user.client_environment_memberships
        .filter(
            client_environment_id=(
                project.client_environment_id
            ),
            is_active=True,
            is_client_admin=True,
            client_environment__is_active=True,
        )
        .exists()
    ):
        return True

    return (
        user.project_memberships
        .filter(
            project=project,
            is_active=True,
            role__catalog_type__code=PROJECT_ROLE_CATALOG,
            role__catalog_type__is_active=True,
            role__code=PROJECT_MANAGER_ROLE,
            role__is_active=True,
        )
        .exists()
    )