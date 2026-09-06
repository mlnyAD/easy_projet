

from apps.projects.models import Project


def can_review_activity_reports(user) -> bool:
    """
    Retourne True si l'utilisateur peut accéder
    à la validation des rapports d'activité.

    Cette fonction détermine uniquement le droit
    fonctionnel d'accéder à la validation.

    Le périmètre des projets consultables est géré
    séparément par ProjectAccessService.
    """

    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    role = user.global_role

    if role is None:
        return False

    if role.catalog_type.code != "USER_GLOBAL_ROLE":
        return False

    if role.code in {
        "SYSTEM_ADMIN",
        "CLIENT_ADMIN",
    }:
        return True

    return Project.objects.filter(
        project_manager=user,
        is_active=True,
    ).exists()